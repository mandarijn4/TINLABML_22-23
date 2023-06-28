import argparse
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
data_dict_rpm = []
data_dict_gear = []
min_accel = 0.0
max_accel = 1.0
temp_accel = 0.0
temp_steer = 0.0
min_steer = -1.0
max_steer = 1.0


def automatic_transmission(gear, rpm):
    """This function will automatically gear up and down"""
    if rpm > 8000:
        gear += 1
    elif rpm < 2500:
        gear -= 1
    if gear < 1:
        gear = 1
    return gear


def drive_example(c):
    S, R = c.S.d, c.R.d
    look_ahead_dist = 60
    target_speed = 250  # 180
    data_dict_angle.append(S['angle'])
    data_dict_speed.append(S['speedX'])
    data_dict_track.append(S['track'])
    data_dict_steer.append(R['steer'])
    data_dict_trackpos.append(S['trackPos'])
    data_dict_lapTime.append(S['curLapTime'])
    data_dict_accel.append(R['accel'])
    data_dict_break.append(R['brake'])
    data_dict_rpm.append(S['rpm'])
    data_dict_gear.append(S['gear'])
    global temp_accel, min_accel, max_accel

    R['gear'] = automatic_transmission(R['gear'], S['rpm'])
    # Steer To Center and Corner
    if S['speedX'] < 80:
        R['steer'] = S['angle'] * 15 / PI  # corner
    else:
        R['steer'] = S['angle'] * 25 / PI  # corner
    R['steer'] -= S['trackPos'] * .05  # center

    # Throttle Control for starting the system
    if S['speedX'] < 90:
        R['accel'] = 1
    elif S['speedX'] < target_speed - (R['steer'] * 40) and R['brake'] == 0:
        temp_accel = temp_accel + 0.05
        def accel_constrain(n, minn, maxx): return max(min(n, maxx), minn)
        print("temp_accel: ", temp_accel)
        print("accel constrain: ", accel_constrain(temp_accel, min_accel, max_accel))
        R['accel'] = accel_constrain(temp_accel, min_accel, max_accel)
    else:
        R['accel'] -= .05

    if S['speedX'] < 80 and S['speedX'] > 55:
        look_ahead_dist = 25
    elif S['speedX'] < 55:
        look_ahead_dist = 10
    elif S['speedX'] > 80 and S['speedX'] < 100:
        look_ahead_dist = 40
    elif S['speedX'] > 130:
        look_ahead_dist = 110
    elif S['track'][2] > 40 or S['track'][15] > 40:
        look_ahead_dist = 6
    else:
        look_ahead_dist = 80

    if S['track'][9] < look_ahead_dist * 2 and S['track'][10] < look_ahead_dist * 2 and S['track'][11] < look_ahead_dist * 2 and S['speedX'] > 160:
        R['accel'] = 0
        temp_accel = 0.0
    elif S['track'][9] < look_ahead_dist * 2 and S['track'][10] < look_ahead_dist * 2 and S['track'][11] < look_ahead_dist * 2 and S['speedX'] > 50:
        temp_accel = 0.3
        R['accel'] = temp_accel
    if S['track'][2] > 40 or S['track'][15] > 40:
        temp_accel = 0.5
        R['accel'] = temp_accel
        R['brake'] = 0
    elif S['track'][9] < look_ahead_dist and S['track'][10] < look_ahead_dist and S['track'][11] < look_ahead_dist and S['speedX'] > 50:
        R['brake'] += 0.03
        R['accel'] = 0
        temp_accel = 0.0
    elif S['track'][4] > 40 and S['speedX'] > 40:
        temp_accel = 0.8
        R['accel'] = temp_accel
        R['brake'] = 0
    else:
        R['brake'] = 0

    # out of the track
    if S['trackPos'] > 1:
        R['steer'] = -0.8
        R['accel'] = 0.3
    elif S['trackPos'] < -1:
        R['steer'] = 0.8
        R['accel'] = 0.3

    print("angle: ", S['angle'])
    print("trackPos: ", S['trackPos'])
    print("track: ", S['track'])
    print("accel: ", R['accel'])
    print("brake: ", R['brake'])
    print("steer: ", R['steer'])
    print("Track 10: ", S['track'][10], "\n")
    return


def new_driver(c):
    S, R = c.S.d, c.R.d
    global temp_steer, min_steer, max_steer

    R['gear'] = automatic_transmission(R['gear'], S['rpm'])
    # Steer To Corner
    R['steer'] = S['angle'] * 25 / PI
    # Steer To Center
    R['steer'] -= S['trackPos'] * .35

    if S['track'][5] < S['track'][14] and S['track'][10] < 80:
        print("corner ahead to the right")
        R['steer'] = -.5
        print(S['track'][14] - S['track'][5])
    elif S['track'][5] > S['track'][14] and S['track'][10] < 80:
        print("corner ahead to the left")
        print(S['track'][5] - S['track'][14])
        R['steer'] = .5
    else:
        print("no corner ahead")
        R['steer'] = 0

    R['accel'] = 1.0
    if S['track'][10] < 200 and S['track'][10] > 150:
        R['accel'] = 0
    elif S['track'][10] < 150 and S['track'][10] > 100 and S['speedX'] > 100:
        R['brake'] = .1
    elif S['track'][10] < 100 and S['track'][10] > 50 and S['speedX'] > 80:
        R['brace'] = .25
    elif S['track'][10] < 50 and S['track'][10] > 20 and S['speedX'] > 60:
        R['brake'] = .5
    if S['speedX'] < 50:
        R['brake'] = 0

    print("Steer: ", R['steer'])


def ai_driver(c):
    S, R = c.S.d, c.R.d
    nn = Neuralnet()
    par = []
    par.append(S['angle'])
    par.append(S['trackPos'])
    par.append(S['speedX'])
    par = par + S['track']
    print([par])
    nn_actions = nn.get_all_actions_from_neural_net(par)
    R['gear'] = automatic_transmission(R['gear'], S['rpm'])
    R['steer'] = nn_actions[0]
    R['accel'] = nn_actions[1]
    R['brake'] = nn_actions[2]
    print("Steer: ", R['steer'])
    print("Accel: ", R['accel'])
    print("Brake: ", R['brake'])


if __name__ == "__main__":
    print("===============================================")
    parser = argparse.ArgumentParser(description='Give the host and port to connect to server, default: 192.168.56.20:3001')
    parser.add_argument('--host', type=str, default='192.168.56.20', help='ip to connect to Server,   default: 192.168.56.20')
    parser.add_argument('--port', type=int, default=3001, help='Port to connect to Server, default: 3001')
    args = parser.parse_args()
    C = Client(H=args.host, p=args.port)
    count = 0
    for step in range(C.maxSteps, 0, -1):
        C.get_servers_input()
        if step % 3 == 0:
            # drive_example(C)
            # new_driver(C)
            ai_driver(C)
            C.respond_to_server()
    C.shutdown()
    print("===============================================")
    CsvWriter.write_csv_file(data_dict_lapTime, data_dict_angle, data_dict_speed, data_dict_track,
                             data_dict_steer, data_dict_accel, data_dict_break, data_dict_trackpos, 
                             data_dict_rpm, data_dict_gear)
