""" 
import by agent
==============================

"""

import numpy as np
import neurolab as nl
import pickle

# Load the net from a file
with open("save_net.pickle", "rb") as f:
    net = pickle.load(f)

print("net is loaded, do tests: ")

test = [0.00678694, 100.05, 3.93779, 4.08413, 5.16986, 6.93252, 11.7321, 15.6098, 23.5846, 47.1353, 74.4002, 81.1555, 87.8839, 135.784, 33.6182, 22.8448, 17.4009, 10.4681, 7.86914, 6.26491, 6.06244]

print(net.sim([test]))

