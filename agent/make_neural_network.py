""" 
This code is used to make a neural network with the neurolab library.
This network is used for torcs simulator, this is a racing game.
The network will be used to control the car in the game.
In short:
The neural network is trained with the data from the csv file.
The neural network is tested with the data from the csv file.
The neural network is saved to a file for every training(5 times).
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


class Trainingsdata():
    """Load the data from the csv file"""

    def __init__(self, filename):
        self.file = None
        self.file_as_list = []
        # the ranges of the input values for each input
        self.input_ranges = [[-np.pi, np.pi], [-1, 1], [-200, 200], [-1, 1], [0, 1], [0, 1], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200],
                        [0, 200], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200], [0, 200]]
        self.load_file(filename)
        self.make_input_vars()
        self.make_target_vars()

    def load_file(self, file_name):
        """Load the data from the csv file into a list"""
        with open(file_name, newline='') as f:
            reader = csv.reader(f)
            self.file = list(reader)
        # skip the first row with the names of the columns
        # add the track to the list as floats instead of a string
        for row in range(1, len(self.file)):
            file = self.file  # /////////////////////////////////////////////////////////
            file[row] = file[row] + list(file[row][4].replace( "[", "").replace("]", "").replace("\"", " ").split(", "))
            del (file[row][4])  # remove string track
            del (file[row][0])  # remove laptime
            row_as_np_str = np.array(file[row])  # load to numpy array
            row_as_np_float = row_as_np_str.astype(float)  # convert str to floats
            row_as_list = list(row_as_np_float)  # make list
            # add row to list
            self.file_as_list.append(row_as_list)

    def make_input_vars(self):
        """Make the input variables for the neural network"""
        # by removing the output variables get are left with input values
        self.input_vars = copy.deepcopy(self.file_as_list)
        for row in self.input_vars:
            del row[Data.STEER.value:Data.BRAKE.value + 1]
        self.input_vars_ranges = copy.deepcopy(self.input_ranges)
        del self.input_vars_ranges[Data.STEER.value:Data.BRAKE.value + 1]

    def make_target_vars(self):
        # make target variables for the network
        # by removing the input variables get are left with output values
        self.target_vars = copy.deepcopy(self.file_as_list)
        for row in self.target_vars:
            del row[Data.TRACK.value: Data.TRACK.value+Data.TRACK_AMOUNT.value]
            del row[Data.ANGLE.value: Data.SPEED.value + 1]


class Network():
    network = None
    
    def __init__(self, trainings_file):
        """make the neural network and load the trainings data"""
        self.data = Trainingsdata(trainings_file)
        self.make_net()

    def make_net(self, layer_sizes=[23, 15]):
        """Make the neural network, default 2 hidden layers [23, 15]"""
        # add the output layer to the layer sizes
        layer_sizes.append(3)
        # all layers use the tanh activation function
        activation_function = [trans.TanSig()] * len(layer_sizes)
        # define size of the input and output
        net_ci = len(self.data.input_vars_ranges)
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
        self.network = Net(self.data.input_vars_ranges, net_co, layers, connect, train.train_bfgs, error.SSE())
        return self.network

    def train_net(self):
        # train the network with the input and target
        # do this 5 times, with 100 epochs each time
        # test the network after each training
        # then save the network to a file
        filename_counter = 0
        for i in range(5):
            err = self.network.train(self.data.input_vars, self.data.target_vars, goal=0.01, show=50, epochs=100)
            self.calculate_custom_deviation()
            # save the net to a file
            filename_counter += 1
            filename = "neural_network" + str(filename_counter)
            print("file saved as: ", filename)
            with open(filename, "wb") as f:
                f.write(pickle.dumps(self.network))

    def calculate_custom_deviation(self, err_steering=0.1, err_acceleration=0.1, err_brake=0.1):
        """Test the neural network and return the errors for each output"""
        # count errors per output
        error_counter_steering = 0
        error_counter_acceleration = 0
        error_counter_brake = 0
        allowed_error_steering = err_steering
        allowed_error_acceleration = err_acceleration
        allowed_error_brake = err_brake
        for i in range(len(self.data.input_vars)):
            if not -allowed_error_steering < (self.network.sim([self.data.input_vars[i]])[0][0] - self.data.target_vars[i][0]) < allowed_error_steering:
                error_counter_steering += 1
            if not -allowed_error_acceleration < (self.network.sim([self.data.input_vars[i]])[0][1] - self.data.target_vars[i][1]) < allowed_error_acceleration:
                error_counter_acceleration += 1
            if not -allowed_error_brake < (self.network.sim([self.data.input_vars[i]])[0][2] - self.data.target_vars[i][2]) < allowed_error_brake:
                error_counter_brake += 1
        print("error counts steering: ", error_counter_steering)
        print("error counts acceleration: ", error_counter_acceleration)
        print("error counts brake: ", error_counter_brake)
        return [error_counter_steering, error_counter_acceleration, error_counter_brake]

net = Network('file_name_of_your_trainingsdata.csv')
net.train_net()
