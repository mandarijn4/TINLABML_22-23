# TINLABML_22-23

## Dependencies  

-   python 3.8.10
-   neurolab
    -   `pip install neurolab`
-   numpy
    -   `pip install numpy`

## Download
To download the code there are two options:
-   Download the zip file from the github page, on branch agent, and extract it
-   Use the release page to download the latest release

## Folder structure
The folder structure is the following:
-   aalborg.pickle
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

<br>
### Disclaimer
The code is provided as is, without any warranty. Use it at your own risk!
It is tested with the provided dependencies, using different versions may cause unexpected behaviour.