#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Python ver: 3.6
"""
Prefix Graph Adder Generator

Author:     Petr Dvoracek
Abstract:   This script is used for the adder generation based on the prefix graph (see prefix_graph.py)
            Adders: 
                - RippleCarryAdder
                - KoggeStone
                - BrentKung
                - Sklansky
                - LadnerFischer
                - HanCarlson
                - Knowles
                - RippleCarryBrentKung (my adder ^.^)
"""

from prefix_graph import PrefixGraph
from utils import *

class RippleCarryAdder(PrefixGraph):
    """ Creates tree structure for Ripple Carry Adder.

    Pros - used gates
    Cons - delay 
    
    Args: 
        bitwidth (int): the length of the adder in bits 
    Example:
        > bitwidth = 4
        > print(RippleCarryAdder(bitwidth))
        
        1 2 3 
        ------
        0     
          1   
            2 
        ------
        1 2 3 
    """
    def __init__(self, bitwidth):
        super(RippleCarryAdder, self).__init__(bitwidth)
        # Just fill the diagonal.
        for row_index, row in enumerate(self.matrix):
            row[row_index] = row_index

# Holy trinity
class KoggeStone(PrefixGraph):
    """ Creates tree structure for Kogge Stone Adder [KS]

    Kogge Stone calculates carry sum of the prefixes for each output.
    
    Pros 
        - in theory, it is the fastest adder

    Cons
        - cost of the used gates
        - wire length may slow down
    
    Reference: 
        [KS] P. Kogge, and H. Stone "A Parallel Algorithm for the Efficient Solution of a General Class of Recurrence Equations". IEEE Transactions on Computers, C-22, p.p. 783-791, 1973

    Args: 
        bitwidth (int)
    Example:
        > bitwidth = 8
        > print(KoggeStone(bitwidth))
        
        1 2 3 4 5 6 7 
        --------------
        0 1 2 3 4 5 6 
          0 1 2 3 4 5 
              0 1 2 3 
        --------------
        1 2 3 4 5 6 7 
    """
    def __init__(self, bitwidth):
        super(KoggeStone, self).__init__(bitwidth)
        for row_index, row in enumerate(self.matrix):
            starting_index = pow2(row_index) - 1 # Sequence in the loop: 0 1 3 7 15
            last_index = bitwidth - 1              # Indexing in the list in python starts from zero. 
            indexes_seq = range(starting_index, last_index)
            values_seq = range(bitwidth)
            # Fill the row with values
            for index, value in zip(indexes_seq, values_seq):
                row[index] = value

class Sklansky(PrefixGraph):
    """ Creates tree structure for Sklansky Adder [Sklansky]

    Sklansky calculates carry sum of the prefixes for each output. The difference between KoggeStone and Sklansky is in the fanout of nodes.

    Pros
        - Same levels as Kogge Stone 

    Cons
        - Huge fan-out causes more delay than in KS

    Reference: 
        [Sklansky] J. Sklansky, "Conditional sum addition logic", IRE Transactions on Electronic Computers, vol. EC-9, no. 6, pp. 226-231, June 1960.

    Args: 
        bitwidth (int)

    Example:
        > bitwidth = 8
        > print(Sklansky(bitwidth))
        
        1 2 3 4 5 6 7 
        --------------
        0   2   4   6
          1 1     5 5
              3 3 3 3
        --------------
        1 2 3 4 5 6 7 
    """
    def __init__(self, bitwidth):
        super(Sklansky, self).__init__(bitwidth)
        for row_index, row in enumerate(self.matrix):
            shift = pow2(row_index+1)  # Sequence in loop: 2 4 8 16 32..
            repeats = pow2(row_index) # How many times is the value repeated? Sequence in loop: 1 2 4 8 16
            starting_index = repeats - 1 # Sequence 0 1 3 7 15
            last_index = bitwidth - 1 # len(row)
            for i in range(starting_index, last_index, shift):
                for j in range(repeats):
                    try:
                        row[j+i] = i
                    except IndexError:
                        pass

class BrentKung(PrefixGraph):
    """ Creates tree structure for Brent Kung Adder [BrentKung] 
    
    Calculates prefix tree for the last output. Then creates inverse tree for the obtaining the rest values. 
    
    Pros
        - small fanout
        - small wiring 
    Cons 
        - more delay 

    Reference:
        [BrentKung] R. Brent and H. Kung, "A regular layout for parallel adders", IEEE Transaction on Computers, vol. C-31, No. 3, pp. 260-264, March 1982.

    Args: 
        bitwidth (int)  bit length of the adder
        
    Example:
        > bitwidth = 8
        > print(BrentKung(bitwidth))
        
        1 2 3 4 5 6 7 
        --------------
        0   2   4   6
            1       5
                    3
                3    
          1   3   5  
        --------------
        1 2 3 4 5 6 7 
    """
    def __init__(self, bitwidth):
        super(BrentKung, self).__init__(bitwidth)
        log2_bitwidth = log2(bitwidth-1) # Upsweep length for BK 
        """ Creates the prefix tree.         
        bit: 1 2 3 4 5 6 7                   1 2 3 4 5 6 7 
           [[0   2   4   6]     indexes => [[0   2   4   6] << Shift is equal to two. 
            [    1       5]                 [    2       6] << Shift is equal to four.
            [            3]] <= values      [            6] << Shift is equal to eight. 
        """
        bitwidth_i = bitwidth - 1  # Counting from 0 
        for idx_row in range(log2_bitwidth):
            shift_length = pow2(idx_row + 1)  # Shift lenght; Sequence in the loop 2, 4, 8, 16..
            starting_index = shift_length - 2  # Starting indexes in the matrix; Sequence in the loop 0 2 6 14 ... 
            starting_value = pow2(idx_row) - 1 # Starting values in the matrix; Sequence in the loop 0 1 3 7 15(shift_length/2 - 1)
            # Mades the row values and indexes sequences
            values_seq = list(range(starting_value, bitwidth_i, shift_length))
            indexes_seq = list(range(starting_index, bitwidth_i, shift_length))
            if not indexes_seq: # There is no other index 
                continue
                # If the root of prefixtree wasnt saved yet. The index (bitwidth) is not power of two. 
                #indexes_seq = [bitwidth_i - 1] # Save the right-most index {The index of index -> (-1 -1)} 
            # Fill the row
            for index, val in zip(indexes_seq, values_seq):
                self.matrix[idx_row][index] = val
        """ Creates the inverse tree. 
        bit: 1 2 3 4 5 6 7                   1 2 3 4 5 6 7 
           [[        3    ]     indexes => [[        4    ]  # Start 
            [  1   3   5  ]] <= values      [  1   3   5  ]  # Start 1, shift 2
        """
        for idx_row in range(1, log2_bitwidth + 1): 
            shift = 2 ** idx_row # Sequence  2 4 8 16 32
            values_start = shift - 1 # Sequence 1 3 7 15
            indexes_start = (-4 + 3 * (2 ** idx_row)) // 2  # Sequence 1 4 10 22 46 etc.
            values = range(values_start, bitwidth_i, shift) 
            indexes = range(indexes_start, bitwidth_i, shift)
            # Fill the row
            for index, val in zip(indexes, values):
                self.matrix[-idx_row][index] = val  # Do not manipulate with idx_row, else it will not be usable for Lander Sklansky and Han Carlson adders


        
class LadnerFischer(BrentKung):
    """ Creates tree structure for LadnerFischer Adder [LadnerFischer] 

    Combination of Sklansky and Brent Kung Adders
    First phase: calculates prefix tree for the last output; but the tree is cut into two halves depending on the level. 
    Second phase: Sklansky adder with shifted values; depending on how many levels have the first phase. 
    Third Phase: inverse prefix tree for the obtaining the rest values. 
    
    Pros
        - small wiring 
        - smaller fanout than Sklansky
    Cons 
        - more delay than Sklansky

    Reference:
        [LadnerFischer] R. E. Ladner, M J. Fischer, "Parallel Prefix Computation", J. Ass. Comput. Mach., vol. 27, pp. 831-838, October 1980.
        
    Args: 
        bitwidth (int)  bit length of the adder
        levels (int)    depth of the prefix tree and inverse tree 
                            levels = 1 means leaves of BK remains; (first and last row become unchanged)
                            levels = log2(bitwidth) means whole tree remains, thus the adder is equal to brentkung.
        
    Example:
        > bitwidth = 16
        > levels = 2
        > print(LadnerFischer(bitwidth, levels))
        
        1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 
        ------------------------------------
        0   2   4   6   8    10    12    14 
            1       5         9          13 
                    2                    10 
                              6           6 
                3       7          11       
          1   3   5   7    9    11    13    
        ------------------------------------
        1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 
    """
    def __init__(self, bitwidth, levels=1):
        if levels <= 0:
            raise AttributeError("Attribute 'levels' must be positive integer, got {levels}.")
        # Create BrentKung
        super(LadnerFischer, self).__init__(bitwidth)
        log2_bitwidth = log2(bitwidth-1)
        levels = log2_bitwidth if (log2_bitwidth - 2) < levels else levels 
        # Reset some rows
        dont_remove = self.matrix[:levels] + self.matrix[-levels:]
        for row_idx, row in enumerate(self.matrix):
            if row not in dont_remove:
                self.matrix[row_idx] = [None for _ in row]
        # Sklansky algorithm, but with shifted values.
        for row_index, row in enumerate(self.matrix[levels:], start=levels):
            if row_index > (levels + log2_bitwidth): break
            repeats = pow2(row_index - levels) # For repeating the value
            starting_value = pow2(row_index) - 1 
            shift = pow2(row_index + 1)
            ladner_shift = pow2(levels)
            for val in range(starting_value, bitwidth, shift):
                for repeat in range(repeats):
                    try:
                        row[val+ladner_shift*(repeat+1) - 1] = val 
                    except IndexError:
                        break # Index error happens. 
        
class HanCarlson(BrentKung):
    """ Creates tree structure for HanCarlson Adder [HanCarlson] 

    Combination of KoggeStone and Brent Kung Adders

    First phase: calculates prefix tree for the last output; but the tree is cut into two halves depending on the level. 
    Second phase: Kogge stone adder with shifted values; depending on how many levels have the first phase. 
    Third Phase: inverse prefix tree for the obtaining the rest values. 
    
    Pros
        - less wiring tracks thang KoggeStone Adder
        - due to less wiring tracks, it may be faster than KoggeStone adder [HanCarlson]
    Cons 
        - in theory, more delay than KoggeStone, however wiring plays the role too :) 
        - not suitable for small adders

    Reference:
        T. Han, D. A. Carlson, "Fast area-efficient VLSI adders", Proc. IEEE 8th Symp. Comput. Arith. (ARITH), pp. 49-56, 1987-May-18–21.
        
    Args: 
        bitwidth (int)  bit length of the adder
        levels (int)    depth of the prefix tree and inverse tree 
                            levels = 1 means leaves of BK remains; (first and last row become unchanged)
                            levels = log2(bitwidth) means whole tree remains, thus the adder is equal to brentkung.

    Example:
        > bitwidth = 16
        > levels = 2
        > print(HanCarlson(bitwidth, levels))
        
        1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 
        ------------------------------------
        0   2   4   6   8    10    12    14 
            1       5         9          13 
                    3         7          11 
                              3           7 
                3       7          11       
          1   3   5   7    9    11    13    
        ------------------------------------
        1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 
    """
    def __init__(self, bitwidth, levels=1):  # works for 1, 2 = lvl; todo fix it
        if levels <= 0:
            raise AttributeError("Attribute 'levels' must be positive integer, got {levels}.")
        # Create BrentKung
        super(HanCarlson, self).__init__(bitwidth)
        log2_bitwidth = log2(bitwidth-1) # Upsweep length for BK 
        levels = log2_bitwidth if (log2_bitwidth - 2) < levels else levels
        # Reset some rows
        dont_remove = self.matrix[:levels] + self.matrix[-levels:]
        for row_idx, row in enumerate(self.matrix):
            if row not in dont_remove:
                self.matrix[row_idx] = [None for _ in row]


        # Kogge stone like with shifted values
        for row_index, row in enumerate(self.matrix[levels:], start=levels):
            kogge_shift = pow2(levels)
            shift = pow2(row_index) - 1  # 2^index
            indexes = range(kogge_shift - 1 + shift, bitwidth-1, kogge_shift)
            values = range(kogge_shift - 1,bitwidth, kogge_shift)
            for i, value in zip(indexes, values):
                row[i] = value

class Knowles(KoggeStone):
    """ Creates tree structure for Knowles Adder [Knowles] 
    
    This Adder is combination of KoggeStone and Sklansky adder.

    Args: 
        bitwidth (int)  bit length of the adder
        max_fanout (int)  max_fanout of Knowles adder (in the contradiction with max_wiring)
                          reduces fanout
        max_wiring (int)  max_wiring of Knowles adder (in the contradictino with max_fanout)
                          reduces wiring
        fanout_list (tuple)  Make the fanouts by yourself (doesnt support variable fanouts in the row)
    
    Examples
        > print(Knowles(8))  # maxwiring = pow2(bitwidth/2)
        
        1 2 3 4 5 6 7 
        --------------
        0 1 2 3 4 5 6 
          0 1     4 5 
              3 3 3 3 
        --------------
        1 2 3 4 5 6 7 


        > print(Knowles(16, max_wiring=4))
        1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 
        ------------------------------------
        0 1 2 3 4 5 6 7 8  9 10 11 12 13 14 
          0 1 2 3 4 5 6 7  8  9 10 11 12 13 
              0 1 2 3            8  9 10 11 
                      7 7  7  7  7  7  7  7 
        ------------------------------------
        1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 
        

        >print(Knowles(16, fanout_list=(1,1,1,2)))
        1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 
        ------------------------------------
        0 1 2 3 4 5 6 7 8  9 10 11 12 13 14 
          0 1 2 3 4 5 6 7  8  9 10 11 12 13 
              0 1 2 3 4 5  6  7  8  9 10 11 
                      1 1  3  3  5  5  7  7 
        ------------------------------------
        1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 

    Reference:
        S. Knowles, "A Family of Adders", Proc. 14th IEEE Symp. Comput. Arith., pp. 277-281, 2001-Jun.
    """
    def __init__(self, bitwidth, max_wiring=None, max_fanout=None, fanout_list=None):
        super(Knowles, self).__init__(bitwidth)         # Okay we have KoggeStone in the matrix.
        log2_bitwidth = log2(bitwidth-1)
        if fanout_list is None:
            # Both none
            if max_wiring is None and max_fanout is None:
                max_wiring = pow2(log2_bitwidth-2) 
            # max_fanout
            if max_fanout is not None and max_wiring is None:
                val = log2(max_fanout)- 1 # Round to the previous power of two. 
                _ = lambda x, max_val=val: pow2(x) if x < max_val else pow2(val)
                fanout_list = list(map(_, range(log2_bitwidth)))
            # max_wiring
            if max_fanout is None and max_wiring is not None:
                max_wiring -= 1
                val = log2(max_wiring) 
                _ = lambda x, max_val=val: pow2(x) if x > max_val else 1
                fanout_list = list(map(_, range(log2_bitwidth)))
                # NOT OPTIMAL... but who cares
            # both int
            if max_wiring is not None and max_fanout is not None:
                raise NotImplementedError(f"I am sorry.")
        if len(fanout_list) != log2_bitwidth:
            raise AttributeError(f"Depth must be a touple or a list consisted of {log2_bitwidth} integers!")
        if any(is_not_pow2(val) for val in fanout_list): # However
            raise AttributeError(f"An integer in fanout list, `{fanout_list}`, is not power of two!")
        if any(pow2(idx) < val for idx, val in enumerate(fanout_list)):
            raise AttributeError(f"Maximum values in fanout list for each element are [1, 2, 4, 8, .. pow2(x)], got {fanout_list}!")
        # Sklansky like adder, 
        for row_index, row, fanout in zip(range(len(self.matrix)), self.matrix, fanout_list):
            # Skip first row
            if row_index == 0:
                continue
            # Edit nodes
            prev_val = None
            for col_index, val in enumerate(row):
                if val is None or val == prev_val: 
                    continue
                # Save the value and overwrite with it the next indexes
                prev_val = val + fanout-1
                for i in range(fanout):
                    try:
                        self.matrix[row_index][col_index + i] = prev_val
                    except IndexError:
                        break
            # Remove redundant gates from the previous row
            if fanout == pow2(row_index):
                previous_row = row_index - 1
                counter = 0
                for col_index, val in enumerate(self.matrix[previous_row]):
                    if val is None:
                        continue
                    if counter > fanout//2 - 1 :
                        try:
                            self.matrix[previous_row][col_index] = None
                        except IndexError:
                            break
                    counter = (counter + 1) % fanout 

class RippleCarryBrentKung(BrentKung):
    """ RippleCarryBrentKung adder

    This Adder is combination of BrentKung and RippleCarry.

    - Lowers delay of RippleCarry adder
    - Composed of less gates than BrentKung adder

    Delay - levels * 2 + bitwidth/(2^levels) - 1       for levels < log2(bitwidth)

    Args: 
        bitwidth (int)  bit length of the adder
        levels (int)    depth of the prefix tree and inverse tree 
                            levels = 1 means that only leaves of BK remains; (first and last row become unchanged)
                            levels = log2(bitwidth) means whole tree remains, thus the adder is equal to brentkung.
    
    Examples:
        
        > RippleCarryBrentKung(8, 1)
        
        1 2 3 4 5 6 7 
        --------------
        0   2   4   6 
            1         
                3     
                    5 
          1   3   5   
        --------------
        1 2 3 4 5 6 7 
        
        
        > RippleCarryBrentKung(16, 2)
        
        1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 
        ------------------------------------
        0   2   4   6   8    10    12    14 
            1       5         9          13 
                    3                       
                              7             
                                         11 
                3       7          11       
          1   3   5   7    9    11    13    
        ------------------------------------
        1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 

    Reference: 
        This is the original. (Let me know if there is an aritcle in which this method is described.)
    """
    def __init__(self, bitwidth, levels=1):
        super(RippleCarryBrentKung, self).__init__(bitwidth)
        log2_bitwidth = log2(bitwidth-1) # Upsweep length for BK 
        levels = log2_bitwidth if (log2_bitwidth - 2) < levels else levels
        # Null some rows in Brent Kung
        dont_remove = self.matrix[:levels] + self.matrix[-levels:]
        for row_idx, row in enumerate(self.matrix):
            if row not in dont_remove:
                self.matrix[row_idx] = [None for _ in row]
        
        for row_index, row in enumerate(self.matrix[levels:], start=levels):
            index = pow2(levels+1) - 2 + pow2(levels)*(row_index - levels)
            value = (pow2(levels) - 1) + pow2(levels)*(row_index-levels)
            try: # if index < bitwidth-1:
                self.matrix[row_index][index] = value
            except IndexError: #else:
                break
print(KoggeStone(8).cgp_nodes())
# End of file
