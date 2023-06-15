""" 
Make neural network for torcs agent

"""

import numpy as np
import neurolab as nl
import pickle
import csv
from enum import Enum
import copy

from neurolab.core import Net
from neurolab import trans, layer, train, error, init

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
    """Load the data from the csv file"""	
    file = None
    file_as_list = []
    # the ranges of the input values for each input
    input_ranges = [[-np.pi, np.pi], [-1, 1], [-200, 200], [-1, 1], [0,1], [0,1], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200]]

    def loadFile(self):
        with open('speedway1.1.csv', newline='') as f:
            reader = csv.reader(f)
            self.file = list(reader)
        # skip the first row with the names of the columns
        # add the track to the list as floats instead of a string
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
if True:
    net = nl.net.newff(input_ranges, [23, 15, 3])
    # minmax = input_ranges
    # size = [30, 15, 3]
    # transf=None

    # net_ci = len(minmax)
    # net_co = size[-1]

    # if transf is None:
    #     transf = [trans.TanSig()] * len(size)
    # assert len(transf) == len(size)

    # layers = []
    # for i, nn in enumerate(size):
    #     layer_ci = size[i - 1] if i > 0 else net_ci
    #     l = layer.Perceptron(layer_ci, nn, transf[i])
    #     l.initf = init.initnw
    #     layers.append(l)
    # connect = [[i - 1] for i in range(len(layers) + 1)]

    # net = Net(minmax, net_co, layers, connect, train.train_bfgs, error.SSE())

else:
    with open("aalborg17.pickle", "rb") as f:
        net = pickle.load(f)

def test_neural_net():
    """Test the neural network and return the errors for each output"""
    # count all errors
    error_counter_steering = 0
    error_counter_acceleration = 0
    error_counter_brake = 0
    allowed_error_steering = 0.1
    allowed_error_acceleration = 0.1
    allowed_error_brake = 0.1

    for i in range(len(input)):
        if not -allowed_error_steering < (net.sim([input[i]])[0][0] - target[i][0]) < allowed_error_steering:
            error_counter_steering += 1
        if not -allowed_error_acceleration < (net.sim([input[i]])[0][1] - target[i][1]) < allowed_error_acceleration:
            error_counter_acceleration += 1
        # if not -allowed_error_brake < (net.sim([input[i]])[0][2] - target[i][2]) < allowed_error_brake:
        if net.sim([input[i]])[0][2] + allowed_error_brake < target[i][2]: # only count is brake is less than target
            error_counter_brake += 1

    print("error counts steering: ", error_counter_steering)
    print("error counts acceleration: ", error_counter_acceleration)
    print("error counts brake: ", error_counter_brake)
    return [error_counter_steering, error_counter_acceleration, error_counter_brake]
# train the network with the input and target
# do this 10 times, with 50 epochs each time
# show the error every 25 epochs
# test the network after each training
counter = 
for i in range(10):
    # activation function is sigmoid tanh
    # error/loss function is sum of squares
    # train function is gradient descent
    err = net.train(input, target, goal=0.01, show=10, epochs=10)
    test_neural_net()
    # save the net to a file
    counter += 1
    print("file saved counter: ", counter)
    with open("speedway" + str(counter) + ".pickle", "wb") as f:
        f.write(pickle.dumps(net))
""
print("output: ", net.sim([input[0]]), target[0])

# # save the net to a file
# with open("aalborg19.pickle", "wb") as f:
#     f.write(pickle.dumps(net))

# print("net is made and saved")





