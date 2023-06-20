import pickle


class Neuralnet():
    """This class loads the neural network from the file neural_network,
    by calling the functions of this class a response is given from the neural network"""

    def __init__(self):
        with open("agent/neural_network", "rb") as f:
            self.neural_network = pickle.load(f)

    def get_all_actions_from_neural_net(self, input_data):
        """Get all actions from the neural network like this: [steering, acceleration, brake]"""
        return self.neural_network.sim([input_data])[0]

    def get_steering(self, par):
        """Get steering from the neural network"""
        return self.neural_network.sim([par])[0][0]

    def get_acceleration(self, par):
        """Get acceleration from the neural network"""
        return self.neural_network.sim([par])[0][1]

    def get_brake(self, par):
        """Get brake from the neural network"""
        return self.neural_network.sim([par])[0][2]
