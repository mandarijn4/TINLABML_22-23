""" 
ADD THIS FILE TO THE SAME FOLDER AS THE AGENT
==============================

"""

import numpy as np
import neurolab as nl
import pickle

class Neuralnet():
    def __init__(self):
        with open("aalborg.pickle", "rb") as f: #
            self.netACCELBRAKESTEER = pickle.load(f)

    def get_steering(self, par):
        return self.netACCELBRAKESTEER.sim([par])[0][0]

    def get_acceleration(self, par):
        return self.netACCELBRAKESTEER.sim([par])[0][1]

    def get_brake(self, par):
        return self.netACCELBRAKESTEER.sim([par])[0][2]
    
""" ADD THIS TO THE AGENT.PY !!!!"""

# from neuralnet import Neuralnet

""" ADD THIS TO THE FUNCTION def drive_example(c): """
# par = []
# par.append(S['angle'])
# par.append(S['trackPos'])
# par.append(S['speedX'])
# par = par + S['track']
# print([par])
# R['steer'] = nn.get_steering(par) 
# R['accel'] = nn.get_acceleration(par)
# R['brake'] = nn.get_brake(par)



