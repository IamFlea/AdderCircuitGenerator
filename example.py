#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Python ver: 3.6

from adders import * 
print("KoggeStone 16 bitwidth")
print(KoggeStone(16))
print("\nSklansky 15 bitwidth")
print(Sklansky(15))
print("\nBrentKung 10 bitwidth")
print(BrentKung(10))
print("\nLadnerFischer 64 bitwidth, 2 levels")
print(LadnerFischer(64, 2))
print("\nHanCarlson 32 bitwidth, 2 levels")
print(HanCarlson(32, 2))
print("\nKnowles 16 bitwidth, 4 max_wiring")
print(Knowles(16, max_wiring=4))
print("\nKnowles 16 bitwidth, 4 max_fanout")
print(Knowles(16, max_fanout=4))
print("\nKnowles 16 bitwidth, 4 max_fanout AND 4 max_wiring (Should print that it is not implemented)")
try:
    print(Knowles(16, max_fanout=4, max_wiring=4))
except NotImplementedError:
    print("This is not implemented")
print("\nKnowles 16 bitwidth custum fanouts and wirings")
print(Knowles(16, fanout_list=(1,1,4,2)))
print("BrentKung 8 bitwidth")
print(BrentKung(8).toPseudocode())
print(BrentKung(8).toPseudocode(False)) # swap the endians
#eof