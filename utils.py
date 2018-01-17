#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" Utility functions"""
pow2 = lambda x: (2**x) 

log2 = lambda x: x.bit_length()

is_pow2 = lambda x: (x & (x - 1)) == 0  # is the number in the sequence: 1 2 4 8 16 32 64... 2^n? 

is_not_pow2 = lambda x: (x & (x - 1)) != 0  # is not the number in the sequence: 1 2 4 8 16 32 64... 2^n? 




