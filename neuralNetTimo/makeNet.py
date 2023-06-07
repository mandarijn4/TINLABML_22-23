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
    SPEED = 1
    STEER = 2
    ACCEL = 3
    BRAKE = 4
    TRACK = 5
    TRACK_AMOUNT = 19

class DataFile():
    file = None
    file_as_list = []

    input_ranges = [[-np.pi, np.pi], [-200, 200], [-1, 1], [0,1], [0,1], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200]]

    def loadFile(self):
        with open('aalborg_3laps.csv', newline='') as f:
            reader = csv.reader(f)
            self.file = list(reader)

        for row in range(1, len(self.file)):
            file = self.file
            file[row] = file[row] + list(file[row][3].replace("[", "").replace("]", "").replace("\"", " ").split(", "))
            del (file[row][3]) # remove string track
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
    del row[Data.STEER.value: Data.BRAKE.value + 1]

input_vars_ranges = copy.deepcopy(DataFile.input_ranges)
del input_vars_ranges[Data.STEER.value: Data.BRAKE.value + 1]

# # remove inputs -> target values
# target_vars = copy.deepcopy(data.file_as_list)
# for row in target_vars:
#     del row[Data.TRACK.value:Data.TRACK.value+Data.TRACK_AMOUNT.value]
#     del row[Data.ANGLE.value: Data.SPEED.value + 1]

target_vars = copy.deepcopy(data.file_as_list)
for row in target_vars:
    del row[Data.ACCEL.value:Data.ACCEL.value+Data.TRACK_AMOUNT.value+2]
    del row[Data.ANGLE.value: Data.SPEED.value + 1]

# input = input_vars[100:10000]
# target = target_vars[100:10000]
input = input_vars
target = target_vars
input_ranges = input_vars_ranges

# print("_______")
# print(target)
# Create network with 21 inputs, 0 neurons in input layer and 3 in output layer

# net = nl.net.newelm(input_ranges, [3])
net = nl.net.newff(input_ranges, [1])
err = net.train(input, target, show=10)

# test = [0.00678694, 100.05, 3.93779, 4.08413, 5.16986, 6.93252, 11.7321, 15.6098, 23.5846, 47.1353, 74.4002, 81.1555, 87.8839, 135.784, 33.6182, 22.8448, 17.4009, 10.4681, 7.86914, 6.26491, 6.06244]
for i in range(0, len(target), 10):
    test = input[i]
    if target[i] - net.sim([test]) > 0.01:
        print(i, target[i], net.sim([test]))

# save the net to a file
with open("save_net.pickle", "wb") as f:
    f.write(pickle.dumps(net))

print("net is made and saved")





