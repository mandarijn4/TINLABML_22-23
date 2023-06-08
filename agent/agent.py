import sys
import numpy as np
from dataLogger import CsvWriter
from client import Client
from neuralnet import Neuralnet

PI = 3.14159265359

data_dict_angle = []
data_dict_speed = []
data_dict_track = []
data_dict_steer = []
data_dict_accel = []
data_dict_trackpos = []
data_dict_break = []
data_dict_lapTime = []
min_accel = 0.0
max_accel = 1.0
temp_accel = 0.0

# Initialize help messages
ophelp = 'Options:\n'
ophelp += ' --host, -H <host>    TORCS server host. [localhost]\n'
ophelp += ' --port, -p <port>    TORCS port. [3001]\n'
ophelp += ' --id, -i <id>        ID for server. [SCR]\n'
ophelp += ' --steps, -m <#>      Maximum simulation steps. 1 sec ~ 50 steps. [100000]\n'
ophelp += ' --episodes, -e <#>   Maximum learning episodes. [1]\n'
ophelp += ' --track, -t <track>  Your name for this track. Used for learning. [unknown]\n'
ophelp += ' --stage, -s <#>      0=warm up, 1=qualifying, 2=race, 3=unknown. [3]\n'
ophelp += ' --file, -f <name>    parameter file name [default_parameters]\n'
ophelp += ' --debug, -d          Output full telemetry.\n'
ophelp += ' --help, -h           Show this help.\n'
ophelp += ' --version, -v        Show current version.\n'
ophelp += ' --rounds, -r         Total number of rounds.\n'
usage = 'Usage: %s [ophelp [optargs]] \n' % sys.argv[0]
usage = usage + ophelp
version = "20130505-2"

# nn = Neuralnet()

def drive_example(c):
    S, R = c.S.d, c.R.d
    look_ahead_dist = 60
    target_speed = 250 #180
    data_dict_angle.append(S['angle'])
    data_dict_speed.append(S['speedX'])
    data_dict_track.append(S['track'])
    data_dict_steer.append(R['steer'])
    data_dict_trackpos.append(S['trackPos'])
    data_dict_lapTime.append(S['curLapTime'])
    data_dict_accel.append(R['accel'])
    data_dict_break.append(R['brake'])
    global temp_accel, min_accel, max_accel

    # Steer To Corner
    R['steer'] = S['angle'] * 10 / PI
    # Steer To Center
    R['steer'] -= S['trackPos'] * .40

    # Throttle Control
    if S['speedX'] < 120: #90
        R['accel'] = 1
    elif S['speedX'] < target_speed - (R['steer'] * 40) and R['brake'] == 0:
        temp_accel = temp_accel + 0.05
        accel_constrain = lambda n, minn, maxx: max(min(n, maxx), minn)
        print("temp_accel: ", temp_accel)
        print("accel constrain: ", accel_constrain(temp_accel, min_accel, max_accel))
        R['accel'] = accel_constrain(temp_accel, min_accel, max_accel)
    else:
        R['accel'] -= .05

    # Traction Control System
    # if ((S['wheelSpinVel'][2] + S['wheelSpinVel'][3]) -
    #         (S['wheelSpinVel'][0] + S['wheelSpinVel'][1]) > 5):
    #     R['accel'] -= .05

    if S['speedX'] < 120:
        look_ahead_dist = 20
    elif S['speedX'] < 140:
        look_ahead_dist = 40
    elif S['speedX'] > 175:
        look_ahead_dist = 80
    elif S['speedX'] > 190:
        look_ahead_dist = 140
    else:
        look_ahead_dist = 60
    if S['track'][9] < look_ahead_dist * 2 and S['track'][10] < look_ahead_dist * 2 and S['track'][11] < look_ahead_dist * 2 and S['speedX'] > 180:
        R['accel'] = 0
        temp_accel = 0.0
    elif S['track'][9] < look_ahead_dist * 2 and S['track'][10] < look_ahead_dist * 2 and S['track'][11] < look_ahead_dist * 2 and S['speedX'] > 50:
        temp_accel = 0.6
        R['accel'] = temp_accel
    if S['track'][9] < look_ahead_dist and S['track'][10] < look_ahead_dist and S['track'][11] < look_ahead_dist and S['speedX'] > 50:
        R['brake'] += 0.03
        R['accel'] = 0
        temp_accel = 0.0
    else:
        R['brake'] = 0
    
    # out of the track
    if S['trackPos'] > 1:
        R['steer'] = -0.8
        R['accel'] = 0.3
    elif S['trackPos'] < -1:
        R['steer'] = 0.8
        R['accel'] = 0.3
    
    # Automatic Transmission
    
    if S['rpm'] > 8000:
        R['gear'] = S['gear'] + 1
    elif S['rpm'] < 2500:
        R['gear'] = S['gear'] - 1

    if R['gear'] < 1:
        R['gear'] = 1

    # if S['speedX'] > 40:
    #     R['gear'] = 2
    # if S['speedX'] > 80:
    #     R['gear'] = 3
    # if S['speedX'] > 110:
    #     R['gear'] = 4
    # if S['speedX'] > 140:
    #     R['gear'] = 5
    # if S['speedX'] > 170:
    #     R['gear'] = 6

    # par = []
    # par.append(S['angle'])
    # par.append(S['trackPos'])
    # par.append(S['speedX'])
    # par = par + S['track']
    # R['steer'] = nn.get_steering(par)
    
    print("angle: ", S['angle'])
    print("trackPos: ", S['trackPos'])
    print("track: ", S['track'])
    print("accel: ", R['accel'])
    print("brake: ", R['brake'])
    print("steer: ", R['steer'], "\n")
    return

if __name__ == "__main__":
    print("===============================================")
    C = Client()
    count = 0
    for step in range(C.maxSteps, 0, -1):
        C.get_servers_input()
        if step % 3 == 0:
            drive_example(C)
            C.respond_to_server()
    C.shutdown()
    print("===============================================")
    CsvWriter.write_csv_file(data_dict_lapTime, data_dict_angle, data_dict_speed, data_dict_track, data_dict_steer, data_dict_accel, data_dict_break, data_dict_trackpos)
