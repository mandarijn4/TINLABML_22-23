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
    # keep angle and speed
    
    # del row[Data.TRACK.value + 11: Data.TRACK.value + Data.TRACK_AMOUNT.value]
    # del row[Data.TRACK.value: Data.TRACK.value + 8]
    # del row[Data.STEER.value: Data.BRAKE.value + 1]
    # del row[Data.SPEED.value]
    # del row[Data.ANGLE.value: Data.POSITION.value + 1]

input_vars_ranges = copy.deepcopy(DataFile.input_ranges)
del input_vars_ranges[Data.STEER.value:Data.BRAKE.value + 1]
# del input_vars_ranges[Data.TRACK.value + 11: Data.TRACK.value + Data.TRACK_AMOUNT.value]
# del input_vars_ranges[Data.TRACK.value: Data.TRACK.value + 8]
# del input_vars_ranges[Data.STEER.value: Data.BRAKE.value + 1]
# del input_vars_ranges[Data.SPEED.value]
# del input_vars_ranges[Data.ANGLE.value: Data.POSITION.value + 1]

# remove inputs -> target values
# target_vars = copy.deepcopy(data.file_as_list)
# for row in target_vars:
#     del row[Data.TRACK.value:Data.TRACK.value+Data.TRACK_AMOUNT.value]
#     del row[Data.ANGLE.value: Data.SPEED.value + 1]

target_vars = copy.deepcopy(data.file_as_list)
for row in target_vars:
    del row[Data.BRAKE.value:Data.BRAKE.value+Data.TRACK_AMOUNT.value+2]
    del row[Data.ANGLE.value: Data.STEER.value + 1]

# input = input_vars[418:433] + input_vars[110:150]
# target = target_vars[418:433] + target_vars[110:150]
input = input_vars
target = target_vars
input_ranges = input_vars_ranges

# for i in range(0,50):
#     print(i, target[i], input[i])

# print("_______")
# print(target)
# Create network with 21 inputs, 0 neurons in input layer and 3 in output layer

net = nl.net.newff(input_ranges, [1])
# net = nl.net.newff(input_ranges, [1])
err = net.train(input, target, goal=0.01, show=10)

# test = [0.00678694, 100.05, 3.93779, 4.08413, 5.16986, 6.93252, 11.7321, 15.6098, 23.5846, 47.1353, 74.4002, 81.1555, 87.8839, 135.784, 33.6182, 22.8448, 17.4009, 10.4681, 7.86914, 6.26491, 6.06244]
for i in range(0, len(target), 10):
    test = input[i]
    if target[i] - net.sim([test]) > 0.01:
        print(i, target[i], net.sim([test]))

# save the net to a file
with open("save_netACCEL.pickle", "wb") as f:
    f.write(pickle.dumps(net))

print("net is made and saved")





