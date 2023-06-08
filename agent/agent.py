import sys
import numpy as np
from dataLogger import CsvWriter
from client import Client

PI = 3.14159265359

data_dict_angle = []
data_dict_speed = []
data_dict_track = []
data_dict_steer = []
data_dict_accel = []
data_dict_break = []
data_dict_trackpos = []
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


def drive_example(c):
    S, R = c.S.d, c.R.d
    look_ahead_dist = 80
    target_speed = 180
    data_dict_angle.append(S['angle'])
    data_dict_speed.append(S['speedX'])
    data_dict_track.append(S['track'])
    data_dict_steer.append(R['steer'])
    data_dict_lapTime.append(S['curLapTime'])
    data_dict_accel.append(R['accel'])
    data_dict_break.append(R['brake'])
    data_dict_trackpos.append(S['trackPos'])
    global temp_accel, min_accel, max_accel

    # Steer To Corner
    R['steer'] = S['angle'] * 10 / PI
    # Steer To Center
    R['steer'] -= S['trackPos'] * .10

    # Throttle Control
    if S['speedX'] < 10:
        R['accel'] = 0.9
    elif S['speedX'] < target_speed - (R['steer'] * 50) and R['brake'] == 0:
        temp_accel = temp_accel + 0.01
        accel_constrain = lambda n, minn, maxx: max(min(n, maxx), minn)
        print("temp_accel: ", temp_accel)
        print("accel constrain: ", accel_constrain(temp_accel, min_accel, max_accel))
        R['accel'] = accel_constrain(temp_accel, min_accel, max_accel)
    else:
        R['accel'] -= .01

    # Traction Control System
    if ((S['wheelSpinVel'][2] + S['wheelSpinVel'][3]) -
            (S['wheelSpinVel'][0] + S['wheelSpinVel'][1]) > 5):
        R['accel'] -= .2

    if S['speedX'] < 50:
        look_ahead_dist = 20
    else:
        look_ahead_dist = 60
    if S['track'][9] < look_ahead_dist * 2 and S['track'][10] < look_ahead_dist * 2 and S['track'][11] < look_ahead_dist * 2 and S['speedX'] > 40:
        temp_accel = 0.5
        R['accel'] = temp_accel
    if S['track'][9] < look_ahead_dist and S['track'][10] < look_ahead_dist and S['track'][11] < look_ahead_dist and S['speedX'] > 40:
        R['brake'] += 0.01
        R['accel'] = 0
        temp_accel = 0.0
    else:
        R['brake'] = 0
    
    if S['trackPos'] > 1:
        R['steer'] = -0.8
        R['accel'] = 0.3
    elif S['trackPos'] < -1:
        R['steer'] = 0.8
        R['accel'] = 0.3
    
    # Automatic Transmission
    R['gear'] = 1
    if S['speedX'] > 40:
        R['gear'] = 2
    if S['speedX'] > 80:
        R['gear'] = 3
    if S['speedX'] > 110:
        R['gear'] = 4
    if S['speedX'] > 140:
        R['gear'] = 5
    if S['speedX'] > 170:
        R['gear'] = 6
    
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