#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Python ver: 3.6
"""
Prefix Graph for Tree Adders

Author:     Petr Dvoracek
Abstract:   This script analyzes adders with parallel calculation of carry based  on  the  prefix  
            graph in 2d matrix reprsentation. The script also calculates the error and translates
            the graph into directed acyclic graph suitable  for  Cartesian  Genetic  Programming.
            The result structure can be easily transfered into other languages - VHDL, C etc. 
            
Description:
            Prelimiters
            ===========
            Ripple Carry Adder is the slowest yet the smallest adder user can use. For input bit 
            vectors A, B; and carry vector C, we  calculate  the  sum  via  formulae:     
            a_i XOR b_i XOR c_i = s_i     and    c_i+1 = (a_i AND b_i) OR (c_i AND (a_i OR B_i)),
            for each bit i. 
            
            The problem with the delay solves so called Carry Look Ahead (CLA) adders. In which 
            Carries are obtained by formulaes: 
                p_i = x_i OR y_i
                g_i = x_i AND y_i
                c_1 = g_0 OR p_0 AND c_0  
                c_2 = g_1 OR p_1 AND g_0 OR p_1 AND p_0 AND c_0
                c_3 = g_2 OR p_2 AND g_1 OR p_2 AND p_1 AND g_0 OR p_2 AND p_1 AND p_0 AND c_0
                ...
            where c_0 is carry in. Note that n binary AND gates can be replaced  with  one  n-ary
            gate. 

            Prefix graph
            ============
            In the case of adder design, we abstract the most gates with Propagate  and  Generate 
            signals which are utilized in the CLA adders, see Figure 1 and Figure 2.  
            
            Each node, represents two formulae:
               g_i = g_i OR (p_i and g_i-1)
               p_i = p_i OR p_i-1

                        Fig1: 4-bit Carry Ripple Adder P/G signals
                              Example     Simplified    Matrix
                        bit:  0 1 2 3     0 1 2 3
                              o o o o     o o o o
                              |\| | |      \
                              o o o o     o o o o       [0,  ,  ]
                              | |\| |        \
                              o o o o     o o o o       [ , 1,  ]
                              | | |\|          \
                              o o o o     o o o o       [ ,  , 2]
                              Prefix Sequence: 123

                        Fig2: 4-bit Kogge-Stone Adder P/G signals
                              Example     Simplified    Matrix
                        bit:  0 1 2 3     0 1 2 3
                              o o o o     o o o o       [0, 1, 2]
                              |\|\|\|      \ \ \
                              o o o o     o o o o       [ , 0, 1]
                              |\|\| |      \ \
                              | \ \ |       \ \
                              | |\|\|        \ \
                              o o o o     o o o o       [ ,  ,  ]
                              Prefix Sequence: 32132
            
            Prefix Sequence
            ===============
            In [5], authors presented a more compact datastructure - a string (a one  dimensional 
            list of nodes). This script can transfer the sequence into the  2D  matrix.  However,
            2D matrix representation has larger searchspace  which  allows  to  cross  nontrivial 
            fanin signals. Eg. [[,,2,1][,,,][,,,][,,,]]  and which allows to  create  Kogge-Stone 
            architecture.

            Error calculation
            =================
            The error response of i-th bit is calculated by  the  humming  distance  of  the  P/G
            connection of the previous bits. In other words, i-th output bit must connect to the  
            input P/G  signal of (i-1)-th, (i-2)-th, ... 1st, and 0th bit. The  search  space  of
            n-bit adder is  restricted by user selection: maximum depth -   d: n!^d   and maximum 
            fanout, however the equation with fanout would be complex,  thus  I  did  not  bother 
            about analyzing it.

            Lets have  two  prefix  graphs:  [[0,0,0,0,0,0]]  and  [[0,None,None,None,None,None]]
            In the first, all P/G signals have an access to 0-th bit and in  the  second  one  is 
            connected only the first bit. The mean error of the first adder is  larger  than  the 
            second one. It is caused by propagation of generate signal from the 0th bit  to  n-th
            skipping the previous  n-1  bits. In the result, if we increment a  big  number  then
            the access to 0th bit resets the most significant bits, i.e:  0b1 + 0b1111001 => 0b10  
            the error in this case is 0b1111000. 

            We can create a different way of error calculation which penalizes not having access
            to the most significant previous bits. 
            
References: [1] H. Stone, and P. Kogge: A  Parallel  Algorithm  for  the  Efficient  Solution  of
                a General Class of Recurrence Equations, 1973,  IEEE Transactions on Computers
            [2] D.  Patil,  O.  Azizi,  M.  Horowitz,  R.   Ho   and   R.   Ananthraman:   Robust
                Energy-Efficient Adder Topologies, 2007, 18th IEEE Symposium on ARITH '07
            [3] L. Sekanina: Evolvable Compnents ((doufám že to tam je))
            [4] L. Li, and H. Zhou: On Error Modeling an Analysis of Approximate Adders, 2014,
                IEEE ??
            [5] S. Roy, M. Choudhury, R. Puri and D. Z. Pan,  "Towards  Optimal  Performance-Area 
                Trade-Off in  Adders  by  Synthesis  of  Parallel  Prefix  Structures,"  in  IEEE 
                Transactions on  Computer- Aided  Design  of  Integrated  Circuits  and  Systems, 
                vol. 33, no. 10, pp. 1517-1530, Oct. 2014.

Date:       January 2018


TODO: fan_in > 1
"""
from operator import itemgetter
from copy import deepcopy

# Utility functions
def filter_none(_list):
    """ Filtering """
    return filter(lambda x: x is not None, _list)

class PrefixGraph(object):
    """ PrefixGraph Class

    Represents the prefix graph as 2D matrix. Calculates the stuff.
    
    Arguments: 
        bitwidth - integer representing the bitwidth size

    Object Attributes:
      bitwidth - bitwidth of the adder
      matrix - two dimensional matrix size of `bitwidth` representaning the adder PG signals
      _reached_signals - the sets containing the reached values for each bit

    Object Methods:
      __init__(bitwidth) 
      check_pg_signals() - checks the accessability of PG signals
    
    Object Properties:
      Error metrics
       - error_shd  - evaluates humming distance of PG signals 
       - error_wshd - weighted SHD
    
      Metrics
       - nodes      - the number of the used nodes
       - fanout     - the fan-out of P/G output is the number of gate inputs it drives
       - delay      - the number of rows containing an integer (rows full of `None` values don't count)
       - wiring     - the number of crossings in the column substracted fanout. 
       - diagonal_crosses_verticals - Relative diagonal wire length.
       - vertical_crosses_diagonals - Crossings in the column
       - diagonal_crosses_diagonals - Diagonals only. E.g.  [None, None, 1, 0]
       - crossings  - returns tirplet of the previous crossings

    Example
      adder = PrefixGraph(3)
      adder.matrix = [[0,None,None], [None,1,None], [None,None,2]]
      adder.check_pg_signals()
      > [{0}, {0,1}, {0,1,2}]
      adder.nodes, adder.delay
      > 3, 3
      adder.error_shd
      > 0
    """

    RECALCULATE_PG_SIGNALS = True

    def __init__(self, bitwidth):
        """ Generates an empty Prefix Graph
        
        Args: 
            bitwidth - integer representing the bitwidth size
        """
        super(PrefixGraph, self).__init__()
        if bitwidth <= 0:
            raise AttributeError("Attribute 'bitwidth' must be positive integer, got {bitwidth}.")
        self.bitwidth = bitwidth
        # Creates the two dimensional matrix; One line (and one column) is not necessary
        self.matrix = PrefixGraph._empty_matrix_(bitwidth)
        self._reached_signals = []

    def _empty_matrix_(bitwidth):
        return [[None for i in range(bitwidth - 1)] for _ in range(bitwidth - 1)]

    def check_pg_signals(self):
        """ Checks the tree leaves (P/G signals) for each bit

        Returns:
            The list of sets of the reached values for each bit.
            For the fully functional n-bit adder the result is: [{0},{0,1},{0,1,2}...{0..n-1, n}]
        """
        first_row, rest_rows = self.matrix[0], self.matrix[1:]
        # Evaluate the first row
        init_set = lambda element: set([element]) if element is not None else set()
        reached_values = [init_set(value) for value in first_row] # First row
        reached_values += [set()] # Termination logic, for value - 1
        # Evaluate the rest
        for row in rest_rows:
            # Reversed iterate through cols (n-th bit, to 1st bit)
            for i, value in reversed(list(enumerate(row))):
                try: # Value is not None
                    # And its previous values ((in the case if value == -1; returns empty set))
                    reached_values[i].update(reached_values[value - 1])
                    # Append to the set the value
                    reached_values[i].add(value)
                except TypeError: # Value is None
                    pass
        self._reached_signals = reached_values[:-1] # Remove termination node
        return reached_values[:-1] # Remove termination node

    def verify(self):
        """ Verifies the adder if it is functional. Else raises an error. """
        if not self._reached_signals or PrefixGraph.RECALCULATE_PG_SIGNALS:
            self.check_pg_signals()
        if self.error_shd:
            raise

    @property
    def error_shd(self):
        """ Sum of Humming Distances """
        if not self._reached_signals or PrefixGraph.RECALCULATE_PG_SIGNALS:
            self.check_pg_signals()
        # Calculate the size of sets
        lengths = map(len, self._reached_signals) # [(0), (0,1), (2)] => [1,2,1]
        shd_function = lambda x: x[0]+1 - x[1]
        return sum(map(shd_function, enumerate(lengths)))

    @property
    def error_wshd(self):
        """ Weighted Sum of Humming Distances """
        if not self._reached_signals or PrefixGraph.RECALCULATE_PG_SIGNALS:
            self.check_pg_signals()
        sum_error = 0
        for maxval, signals in enumerate(self._reached_signals):
            error = 0
            for value in reversed(range(maxval+1)):
                if value not in signals:
                    error += value +  1
                elif error:
                    error += (self.bitwidth - value)
            sum_error += error
        return sum_error

    def error_wshd_old(self):
        ranges = [set(range(i+1)) for i in range(self.bitwidth - 1)]
        differences = map(lambda x, y: sum(x - y) + len(x - y), ranges, self._reached_signals)
        return sum(differences)

    @property
    def nodes(self):
        """ Returns Used Nodes """
        used_nodes = lambda row: len(list(filter_none(row)))
        return sum(map(used_nodes, self.matrix))

    @property
    def delay(self):
        """ Evaluate Delay

        Note:
            the count of used rows
        """
        f_used_nodes = lambda row: len(list(filter_none(row)))
        not_zero = lambda value: value != 0
        used_nodes = map(f_used_nodes, self.matrix)
        return len(list(filter(not_zero, used_nodes)))

    @property
    def fanout(self):
        """ Evaluate Fanout """
        max_fanout = 0
        for row in self.matrix:
            for val in filter_none(row):
                fanout = row.count(val)
                max_fanout = fanout if fanout > max_fanout else max_fanout
        return max_fanout

    @property
    def wiring(self):
        max_crossings = 0
        for row in self.matrix:
            for index in range(len(row)):
                filtered = filter(lambda x, val=index: x is not None and x <= val, row[index+1:])
                crossings = len(set(list(filtered)))
                max_crossings = crossings if crossings > max_crossings else max_crossings
        return max_crossings + 1

    @property
    def diagonal_crosses_verticals(self): # Aka wire length.
        """ Wire Crossing A - how many vertical wires are crossed by single diagonal wire? """
        max_crossings = 0
        for row in self.matrix:
            for index, value in enumerate(row):
                try:
                    crossing = index - value
                    max_crossings = crossing if crossing > max_crossings else max_crossings
                except TypeError: # value is None
                    pass
        return max_crossings

    @property
    def vertical_crosses_diagonals(self): # Aka crossing in the column
        """ Wire Crossing B - how many diagonal wires are crossed by single vertical wire? """
        max_crossings = 0
        for row in self.matrix:
            for index in range(len(row)):
                filtered = filter(lambda x, val=index: x is not None and x <= val, row[index+1:])
                crossings = len(list(filtered))
                max_crossings = crossings if crossings > max_crossings else max_crossings
        return max_crossings

    @property
    def diagonal_crosses_diagonals(self): # Diagonals only. E.g.  [None, None, 1, 0]
        """ Wire Crossing C - how many diagonal wires are crossed by another diagonal wire? """
        max_crossings = 0
        for row in self.matrix:
            for index, value in enumerate(row):
                if value is None:
                    continue
                filtered = filter(lambda x, val=value: x is not None and x < val, row[index+1:])
                crossings = len(list(filtered))
                max_crossings = crossings if crossings > max_crossings else max_crossings
        return max_crossings

    @property
    def crossings(self):
        """ Evaluates All Possible Wire Crossings """
        return (self.diagonal_crosses_verticals,
                self.vertical_crosses_diagonals,
                self.diagonal_crosses_diagonals)

    def __str__(self):
        """ For printing """
        empty_space_count = len(str(self.bitwidth - 2))
        result = ""
        for index in range(self.bitwidth - 1):
            result += str(index+1) + " "
        skip = "-" * len(result) + "\n"
        result += "\n" + skip
        for row in self.matrix:
            if all(value is None for value in row):
                continue
            for index, value in enumerate(row):
                result += str(value).replace("None", " ").rjust(len(str(index+1)))
                result += " "
            result += "\n"
        result += skip
        for index in range(self.bitwidth - 1):
            result += str(index+1) + " "
        return result

    def cgp_nodes(self, bigendian=True):
        """ Returns the circuit as a Directed Acyclic Graph with nodes representing an operation
        
        Parameter:
            operations_set
                A list of operations, must contain three strings: "XOR", "AND", "OR"
            bigendian
                Byte order of inputs and output

        Returns: 
            The list of nodes representatning DAG, ended with primary outputs.
        """
        # I know it is rude, but these functions are just used here. 
        def add_node(input_a, input_b, operation):
            """ Translate the operation and creates a node"""
            return [input_a, input_b, operation]
            #return [input_a, input_b, operation]
        def get_last_propagation_row_indexes(matrix):
            """ The last P/G node doesnt need to propagate the signal
            Return
                A list of the row indexes of last P/G signal
            """
            result = deepcopy(self.matrix[-1]) # Copy the last row
            # Iterate through the rows, backwards
            for row_idx, row in reversed(list(enumerate(matrix[:-1]))): 
                for idx, val in enumerate(row): # Iterate through the columns
                    if val is not None and result[idx] is None:
                        result[idx] = row_idx # Save the value
            return result

        # Preprocessing 
        ###############
        bitwidth = self.bitwidth

        # Lists with primary input indexes
        a_inputs = list(range(bitwidth))
        b_inputs = list(range(bitwidth, bitwidth*2)) 
        
        # Result chromosome
        chrom = []
        # Bitwise propagate/generate generation
        # Add generate gates and save their output indexes
        chrom += map(add_node, a_inputs, b_inputs, ["AND"] * bitwidth)
        generate = list(range(bitwidth*2, bitwidth*3))
        # Add propagate gates and save their output indexes
        chrom += map(add_node, a_inputs, b_inputs, ["XOR"] * bitwidth) 
        propagate = list(range(bitwidth*3, bitwidth*4))
        # Save propagate bits for further xoring with the carry bits
        a_xor_b = list(range(bitwidth*3, bitwidth*4))
        # The last P/G node doesnt need to propagate the signal; save their pointers
        dont_propagate = get_last_propagation_row_indexes(self.matrix)

        # Prefix processing
        ###################
        for row_idx, row in enumerate(self.matrix):
            for index, pg in reversed(list(enumerate(row, start=1))):
                # Don't append anything if the pg (previous P/G value) is set to None
                if pg is None:
                    continue
                # Add gates for Generate logic; formula  G_i = G_i OR (G_i-1 AND P_i)
                chrom += [add_node(propagate[index], generate[pg], "AND")]
                chrom += [add_node(generate[index], 2*bitwidth + len(chrom) - 1, "OR")]
                generate[index] = len(chrom) + 2*bitwidth - 1
                if row_idx != dont_propagate[index - 1]:
                    chrom += [add_node(propagate[index], propagate[pg], "AND")]
                    propagate[index] = len(chrom) + 2*bitwidth - 1

        # Postprocessing
        ################
        # Sum generation nodes
        start = len(chrom)
        chrom += map(add_node, a_xor_b[1:], generate[:-1], ["XOR"]*bitwidth)
        _ = list(range(start + 2*bitwidth, len(chrom) + 2*bitwidth))
        # Add output gates
        chrom += [[a_xor_b[0]] + _ + [generate[-1]]]

        # If user wants bigendian, just invert inputs and outputs
        if bigendian:
            for node in chrom:
                if node[0] < 2*bitwidth:
                    node[0] = 2*bitwidth - node[0] - 1
                if node[1] < 2*bitwidth:
                    node[1] = 2*bitwidth - node[1] - 1

            chrom[-1] = chrom[-1][::-1]
        return chrom
# End of file
