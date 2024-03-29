# TINLABML_22-23

## Introduction

For this project we have learned how to use and make a neural network.
We have used the neurolab library to create a neural network that can drive a car on a circuit.
The neural network is trained using a supervised learning method, the neural network is trained on a dataset of driving data(trainingsdata.csv). 
First we made an agent that could drive on the circuit and collect driving/sensor data.
After that we used the collected data to train the neural network.
The neural network is trained to drive the car around the circuit as nice as possible, without crashing.

The network has 22 inputs neurons, 2 dense layers and 3 output neurons. 
The first dense layer has 23 neurons and second dense layer has 15 neurons.

## Dependencies  

-   python 3.8.10
-   neurolab
    -   `pip install neurolab`
-   numpy
    -   `pip install numpy`

### Install dependencies
To install the dependencies you can use the following command:
> `pip install -r requirements.txt`

## Download
To download the code there are two options:
-   Download the zip file from the github page and extract it, then copy the agent folder to where you want to run the agent.
-   Use the release page to download the latest release

## Folder structure
The folder structure is the following:
-   make_neural_network.py
    -   With this file you can create a new network by feeding it trainingsdata
-   neural_network
    -   This file contains the model for running the agent on the circuit
-   agent.py
-   client.py
-   dataLogger.py
-   default_parameters
    -   This file is necessary for setting up the connection to the server
-   driver.py
-   neuralnet.py
-   server.py

## Usage
To use this code you need to have installed all the dependencies listed above.
Than you can run the code with the following command:
-   to start the agent with the default host and port:
    > `python3 agent.py` 
-   to start the agent with a custom port:
    > `python3 agent.py --port 3002`
-   to start the agent with a custom host:
    > `python3 agent.py --host 192.168.2.1` 
-   to start the agent with a custom host and port:
    > `python3 agent.py --host 192.168.2.1 --port 3002`

It is also possible to run the agent with a docker container.
There for a dockerfile is provided.
- To build the docker image you can use the following command:
    > `docker build --pull --rm -f "dockerfile" -t tinlabml_22-23:latest "."`
- To run the docker image you can use the following command:
    > `docker run --rm -it  tinlabml_22-23:latest`
<br>

### Disclaimer
The code is provided as is, without any warranty. Use it at your own risk!
It is tested with the provided dependencies, using different versions may cause unexpected behavior.
