""" 
Simple example of use neurolab
==============================

"""

import numpy as np
import neurolab as nl
import pickle


training_set = [[0,0,0,1,1,1], [0,0,0,0,1,1], [0,0,0,1,0,1], [0,0,0,1,1,0], [1,1,1,0,0,0], [0,1,1,0,0,0], [1,0,1,0,0,0], [1,1,0,0,0,0]]
input = training_set # 2 elements
target = [[0, 1], [0, 1], [0, 1], [0, 1], [1, 0], [1, 0], [1, 0], [1, 0]]

# Create network with 6 inputs, 0 neurons in input layer and 2 in output layer
input_ranges = [[0,1],[0,1],[0,1],[0,1],[0,1],[0,1]]
net = nl.net.newelm(input_ranges, [2])
err = net.train(input, target)

# save the net to a file
with open("save_net.pickle", "wb") as f:
    f.write(pickle.dumps(net))

print("net is made and saved")