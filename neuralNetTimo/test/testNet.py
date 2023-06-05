""" 
Simple example of use neurolab
==============================

"""

import numpy as np
import neurolab as nl
import pickle

input_ranges = [[0,1],[0,1],[0,1],[0,1],[0,1],[0,1]]
net = nl.net.newelm(input_ranges, [2])

# Load the net from a file
with open("save_net.pickle", "rb") as f:
    net = pickle.load(f)

print("net is loaded, do tests: ")

# test
print(net.sim([[1,1,1,0,0,0]]))
print(net.sim([[1,1,0,1,0,0]]))
print(net.sim([[1,1,0,1,1,0]]))
print(net.sim([[0,0,0,1,1,1]]))

