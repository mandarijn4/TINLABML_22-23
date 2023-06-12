""" 
Make neural network for torcs agent

"""

import numpy as np
import neurolab as nl
import pickle
import csv
from enum import Enum
import copy

class Data(Enum):
    ANGLE = 0
    POSITION = 1
    SPEED = 2
    STEER = 3
    ACCEL = 4
    BRAKE = 5
    TRACK = 6
    TRACK_AMOUNT = 19

class DataFile():
    file = None
    file_as_list = []

    input_ranges = [[-np.pi, np.pi], [-1, 1], [-200, 200], [-1, 1], [0,1], [0,1], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200]]

    def loadFile(self):
        with open('speedway1.1.csv', newline='') as f:
            reader = csv.reader(f)
            self.file = list(reader)

        for row in range(1, len(self.file)):
            file = self.file
            file[row] = file[row] + list(file[row][4].replace("[", "").replace("]", "").replace("\"", " ").split(", "))
            del (file[row][4]) # remove string track
            del (file[row][0]) # remove laptime
            row_as_np_str = np.array(file[row]) # load to numpy array
            row_as_np_float = row_as_np_str.astype(float) # convert str to floats
            row_as_list = list(row_as_np_float) # make list
            # add row to list
            self.file_as_list.append(row_as_list)
data = DataFile()

data.loadFile()

# remove output variables -> input values
input_vars = copy.deepcopy(data.file_as_list)
for row in input_vars:
    del row[Data.STEER.value:Data.BRAKE.value + 1]

input_vars_ranges = copy.deepcopy(DataFile.input_ranges)
del input_vars_ranges[Data.STEER.value:Data.BRAKE.value + 1]

# remove input variables -> output values
target_vars = copy.deepcopy(data.file_as_list)
for row in target_vars:
    del row[Data.TRACK.value: Data.TRACK.value+Data.TRACK_AMOUNT.value]
    del row[Data.ANGLE.value: Data.SPEED.value + 1]

input = input_vars
target = target_vars
input_ranges = input_vars_ranges

# Create network with 22 inputs, 0 neurons in input layer and 2 in output layer
if False:
    net = nl.net.newff(input_ranges, [23, 23, 15, 3])
else:
    with open("speedway1.1.pickle", "rb") as f:
        net = pickle.load(f)

# with open("save_net.pickle", "rb") as f:
#     net = pickle.load(f)
err = net.train(input, target, goal=0.01, show=10, epochs=1000)

print("output: ", net.sim([input[0]]))

# save the net to a file
with open("speedway1.1.pickle", "wb") as f:
    f.write(pickle.dumps(net))

print("net is made and saved")





