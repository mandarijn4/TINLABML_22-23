""" 
import by agent
==============================

"""

import numpy as np
import neurolab as nl
import pickle

class Neuralnet():
    def __init__(self):
        with open("save_netACCELBRAKESTEER.pickle", "rb") as f:
            self.netACCELBRAKESTEER = pickle.load(f)

    def get_steering(self, par):
        return self.netACCELBRAKESTEER.sim([par])[0][0]

    def get_acceleration(self, par):
        return self.netACCELBRAKESTEER.sim([par])[0][1]

    def get_brake(self, par):
        return self.netACCELBRAKESTEER.sim([par])[0][2]
    
    def get_all_controls(self,par):
        return self.netACCELBRAKESTEER.sim([par])[0]
    




