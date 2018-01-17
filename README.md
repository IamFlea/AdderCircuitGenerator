# Adders Generator
This project generates and analyses adders with parallel carry calculation based on their prefix graph. 
This script also calculates the error of prefix graph and translates it into the directed acyclic graph suitable for Cartesian Genetic Programming. 
The result node list may be easily transfered into the other languages such as VHDL or C. 



# Prelimiters

**Ripple Carry Adder** is the slowest yet the smallest adder user can use. For input bit vectors `A`, `B`; and carry vector `C`, we calculate the sum via formulae: `a_i XOR b_i XOR c_i = s_i` and `c_i+1 = (a_i AND b_i) OR (c_i AND (a_i OR B_i))`, for each bit `i`. 
            
The problem with the delay solves so called **Carry Look Ahead (CLA) adders**. In which carry values are obtained by formulaes: 
```
p_i = x_i OR y_i
g_i = x_i AND y_i
c_1 = g_0 OR p_0 AND c_0  
c_2 = g_1 OR p_1 AND g_0 OR p_1 AND p_0 AND c_0
c_3 = g_2 OR p_2 AND g_1 OR p_2 AND p_1 AND g_0 OR p_2 AND p_1 AND p_0 AND c_0
...
```
in which `c_0` is a carry in. Note that `n` binary `AND` gates can be replaced with one n-ary gate. 

### Prefix graph
In the case of adder design, we abstract the most gates with Propagate and Generate signals which are utilized in the CLA adders, see Figure 1 and Figure 2, in which each node, represents two formulae:

```
g_i = g_i OR (p_i and g_i-1)
p_i = p_i OR p_i-1
```

Fig1: 4-bit Carry Ripple Adder P/G signals
```
      Example     Simplified    Matrix
bit:  0 1 2 3     0 1 2 3
      o o o o     o o o o
      |\| | |      \
      o o o o     o o o o       [0,  ,  ]
      | |\| |        \
      o o o o     o o o o       [ , 1,  ]
      | | |\|          \
      o o o o     o o o o       [ ,  , 2]
```

Fig2: 4-bit Kogge-Stone Adder P/G signals
```
      Example     Simplified    Matrix
bit:  0 1 2 3     0 1 2 3
      o o o o     o o o o       [0, 1, 2]
      |\|\|\|      \ \ \
      o o o o     o o o o       [ , 0, 1]
      |\|\| |      \ \
      | \ \ |       \ \
      | |\|\|        \ \
      o o o o     o o o o       [ ,  ,  ]
```

We can create a lot of prefix tree graphs representating the adders. Nevertheless, there are three main adders - Brent Kung Adder, Kogge Stone Adder, and Sklansky Adder. Each differs in the terms of area, delay, or power.


## Brent Kung 

The algorithm calculates the prefix tree for the *last* output. Then creates inverse tree for the obtaining the rest values. 

This adder is not the fastest, yet it has the lowest wiring tracks and fanout, which decreases area and delay respectively. 

![Brent Kung](http://slideplayer.com/slide/9189606/27/images/34/Brent-Kung+11:+Adders.jpg)

## Kogge Stone
Kogge Stone creates prefix tree graph for *each* output. 

This adder is considered as one of the fastest and largest (in the terms of area) adder. However in the last level, it has large amount of wiring tracks which may decrease the speed, see picture below.


![Kogge Stone](http://slideplayer.com/slide/5267198/17/images/30/Kogge-Stone+17:+Adders.jpg)


## Sklansky
Sklansky calculates carry sum of the prefixes for each output. 

It is similar to KoggeStone yet the difference between them is in the fanout of nodes. See the last level in the picture below. It may have less used nodes, however, its delay grows with added fanout nodes. 

![Sklansky](http://slideplayer.com/slide/5267198/17/images/29/Sklansky+17:+Adders.jpg)


## Han Carlson
It is a combination of Kogge Stone and Brent Kung. The algorithm is partitioned into the three phases. In the first phase, we create a prefix tree of choosen depth and then we create the inverse tree in the last phase. The second phase has Kogge Stone architecture. 

In the summary, Han Carlson Adders gives us a tradeoff between delay and wiring tracks. Below we can see its architecture with Brent-Kung of level 1.
![Han Carlson](http://slideplayer.com/slide/9189606/27/images/40/Han-Carlson+11:+Adders.jpg)

## Ladner Fischer
Ladner Fischer Adder is a combination of Kogge Stone and Brent Kung. Similary to Han Carlson, the algorithm is partitioned into the three phases. However, the second phase has Sklansky architecture. 

Ladner Fischer Adders give us a tradeoff between delay and fanout. Below we can see the architecture with Brent-Kung of level 1.
![Ladner Fischer](http://slideplayer.com/slide/5267198/17/images/35/Ladner-Fischer+17:+Adders.jpg)

## Knowles 
This Adder is combination of KoggeStone and Sklansky adder. It gives us a tradeoff between wirings and fanouts. 
![Knowles](http://slideplayer.com/slide/5267198/17/images/34/Knowles+[2,+1,+1,+1]+17:+Adders.jpg)

# Usage and Examples
```python
> from adders import *
> bitwidth = 8
> adder = KoggeStone(bitwidth)
> print(adder)
1 2 3 4 5 6 7 
--------------
0 1 2 3 4 5 6 
  0 1 2 3 4 5 
      0 1 2 3 
--------------
1 2 3 4 5 6 7 

> adder.nodes, adder.delay, adder.fanout, adder.wiring
(17, 3, 1, 4)
> adder.cgp_nodes()
[[15, 7, 'AND'], [14, 6, 'AND'], [13, 5, 'AND'], [12, 4, 'AND'], [11, 3, 'AND'], [10, 2, 'AND'], [9, 1, 'AND'], [8, 0, 'AND'], [15, 7, 'XOR'], [14, 6, 'XOR'], [13, 5, 'XOR'], [12, 4, 'XOR'], [11, 3, 'XOR'], [10, 2, 'XOR'], [9, 1, 'XOR'], [8, 0, 'XOR'], [31, 22, 'AND'], [23, 32, 'OR'], [31, 30, 'AND'], [30, 21, 'AND'], [22, 35, 'OR'], [30, 29, 'AND'], [29, 20, 'AND'], [21, 38, 'OR'], [29, 28, 'AND'], [28, 19, 'AND'], [20, 41, 'OR'], [28, 27, 'AND'], [27, 18, 'AND'], [19, 44, 'OR'], [27, 26, 'AND'], [26, 17, 'AND'], [18, 47, 'OR'], [26, 25, 'AND'], [25, 16, 'AND'], [17, 50, 'OR'], [34, 39, 'AND'], [33, 52, 'OR'], [34, 40, 'AND'], [37, 42, 'AND'], [36, 55, 'OR'], [37, 43, 'AND'], [40, 45, 'AND'], [39, 58, 'OR'], [40, 46, 'AND'], [43, 48, 'AND'], [42, 61, 'OR'], [43, 49, 'AND'], [46, 51, 'AND'], [45, 64, 'OR'], [49, 16, 'AND'], [48, 66, 'OR'], [54, 65, 'AND'], [53, 68, 'OR'], [57, 67, 'AND'], [56, 70, 'OR'], [60, 51, 'AND'], [59, 72, 'OR'], [63, 16, 'AND'], [62, 74, 'OR'], [25, 16, 'XOR'], [26, 51, 'XOR'], [27, 67, 'XOR'], [28, 65, 'XOR'], [29, 75, 'XOR'], [30, 73, 'XOR'], [31, 71, 'XOR'], [69, 82, 81, 80, 79, 78, 77, 76, 24]]
```

Result is obtrained by calling `adder.cgp_nodes()` which represents circuit as a list of operations in postfix notation ended by primary outputs. Primary inputs are two ranges of numbers. The first one represents an input vector `A` and its values are in the `range(0, bitwidth)`. The second one represents an input vector `B` and its values are in the `range(bitwidth, bitwidth*2)`. Then we assign indexes to each node in the list starting with `bitwidth*2` to `bitwidth*2 + len(chrom)`. Each node in the list is represented by two integers (pointing to primary inputs or previous node) and its operation. If this is not clear enough, please see some presentation about Cartesian Genetic Programming -- chromosome representation. 

