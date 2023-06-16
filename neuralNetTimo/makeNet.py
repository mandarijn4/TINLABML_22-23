""" 
This code is used to make a neural network with the neurolab library.
This network is used for torcs simulator, this is a racing game.
The network will be used to control the car in the game.
In short:
The neural network is trained with the data from the csv file.
The neural network is tested with the data from the csv file.
The neural network is saved to a file.
"""

import csv
import copy
from enum import Enum
import pickle
import numpy as np
from neurolab.core import Net
from neurolab import trans, layer, train, error, init


class Data(Enum):
    """Enum the columns of the data in the csv file"""
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
    input_ranges = [[-np.pi, np.pi], [-1, 1], [-200, 200], [-1, 1], [0, 1], [0, 1], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200],
                    [0, 200], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200]]

    def load_file(self, file_name):
        """Load the data from the csv file into a list"""
        with open(file_name, newline='') as f:
            reader = csv.reader(f)
            self.file = list(reader)
        # skip the first row with the names of the columns
        # add the track to the list as floats instead of a string
        for row in range(1, len(self.file)):
            file = self.file
            file[row] = file[row] + list(file[row][4].replace(
                "[", "").replace("]", "").replace("\"", " ").split(", "))
            del (file[row][4])  # remove string track
            del (file[row][0])  # remove laptime
            row_as_np_str = np.array(file[row])  # load to numpy array
            row_as_np_float = row_as_np_str.astype(
                float)  # convert str to floats
            row_as_list = list(row_as_np_float)  # make list
            # add row to list
            self.file_as_list.append(row_as_list)


data = DataFile()
data.load_file('speedway1.1.csv')

# make input variables for the network
# by removing the output variables get are left with input values
input_vars = copy.deepcopy(data.file_as_list)
for row in input_vars:
    del row[Data.STEER.value:Data.BRAKE.value + 1]
input_vars_ranges = copy.deepcopy(DataFile.input_ranges)
del input_vars_ranges[Data.STEER.value:Data.BRAKE.value + 1]

# make target variables for the network
# by removing the input variables get are left with output values
target_vars = copy.deepcopy(data.file_as_list)
for row in target_vars:
    del row[Data.TRACK.value: Data.TRACK.value+Data.TRACK_AMOUNT.value]
    del row[Data.ANGLE.value: Data.SPEED.value + 1]


# with 3 layers
# 22 inputs, 23 neurons in the first layer, 15 in the second and 3 in the ouput layer

# Create a neural network with 3 layers
# all layers use the tanh activation function
layer_sizes = [30, 15, 3]
activation_function = [trans.TanSig()] * len(layer_sizes)
# define size of the input and output
net_ci = len(input_vars_ranges)
net_co = layer_sizes[-1]
# make dense layers
layers = []
for i, nn in enumerate(layer_sizes):
    layer_ci = layer_sizes[i - 1] if i > 0 else net_ci
    l = layer.Perceptron(layer_ci, nn, activation_function[i])
    l.initf = init.initnw
    layers.append(l)
connect = [[i - 1] for i in range(len(layers) + 1)]
# error/loss function is sum of squares
# train function is the Broyden Fletcher Goldfarb Shanno (BFGS) method
# https://en.wikipedia.org/wiki/Broyden%E2%80%93Fletcher%E2%80%93Goldfarb%E2%80%93Shanno_algorithm
net = Net(input_vars_ranges, net_co, layers,
          connect, train.train_bfgs, error.SSE())


def calculate_custom_deviation(err_steering=0.1, err_acceleration=0.1, err_brake=0.1):
    """Test the neural network and return the errors for each output"""
    # count errors per output
    error_counter_steering = 0
    error_counter_acceleration = 0
    error_counter_brake = 0
    allowed_error_steering = err_steering
    allowed_error_acceleration = err_acceleration
    allowed_error_brake = err_brake
    for i in range(len(input_vars)):
        if not -allowed_error_steering < (net.sim([input_vars[i]])[0][0] - target_vars[i][0]) < allowed_error_steering:
            error_counter_steering += 1
        if not -allowed_error_acceleration < (net.sim([input_vars[i]])[0][1] - target_vars[i][1]) < allowed_error_acceleration:
            error_counter_acceleration += 1
        if not -allowed_error_brake < (net.sim([input_vars[i]])[0][2] - target_vars[i][2]) < allowed_error_brake:
            error_counter_brake += 1
    print("error counts steering: ", error_counter_steering)
    print("error counts acceleration: ", error_counter_acceleration)
    print("error counts brake: ", error_counter_brake)
    return [error_counter_steering, error_counter_acceleration, error_counter_brake]


# train the network with the input and target
# do this 5 times, with 100 epochs each time
# show the error every 50 epochs
# test the network after each training
filename_counter = 0
for i in range(5):
    err = net.train(input_vars, target_vars, goal=0.01, show=50, epochs=100)
    calculate_custom_deviation()
    # save the net to a file
    filename_counter += 1
    print("file saved counter: ", filename_counter)
    with open("speedway" + str(filename_counter) + ".pickle", "wb") as f:
        f.write(pickle.dumps(net))