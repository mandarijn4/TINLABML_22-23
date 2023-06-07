""" 
import by agent
==============================

"""

import numpy as np
import neurolab as nl
import pickle

class Neuralnet():
    def __init__(self):
        # Load the net from a file
        with open("save_net.pickle", "rb") as f:
            self.net = pickle.load(f)

    def get_steering(self, par):
        return self.net.sim([par])


