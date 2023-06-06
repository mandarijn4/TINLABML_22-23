import math
import socket
import json
import sys
import getopt
import numpy as np
import csv

PI = 3.14159265359

data_dict_angle = []
data_dict_speed = []
data_dict_track = []
data_dict_steer = []
data_dict_accel = []
data_dict_break = []
data_tuple_angle = ()

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


def clip(v, lo, hi):
    if v < lo:
        return lo
    elif v > hi:
        return hi
    else:
        return v

class Client():
    def __init__(self, H=None, p=None, i=None, e=None, t=None, s=None, d=None, f=None, r=None):
        # If you don't like the option defaults,  change them here.
        self.host = 'localhost'
        self.port = 3001
        self.sid = 'SCR'
        self.maxEpisodes = 1  # "Maximum number of learning episodes to perform"
        self.trackname = 'unknown'
        self.stage = 3  # 0=Warm-up, 1=Qualifying 2=Race, 3=unknown <Default=3>
        self.debug = False
        self.maxSteps = 100000  # 50steps/second
        self.maxRounds = 1
        self.pfilename = 'default_parameters'
        self.parse_the_command_line()
        if H: self.host = H
        if p: self.port = p
        if i: self.sid = i
        if e: self.maxEpisodes = e
        if t: self.trackname = t
        if s: self.stage = s
        if d: self.debug = d
        self.S = ServerState()
        self.R = DriverAction()
        self.P = None
        # self.stds = np.load('./model/stds.npy', allow_pickle=True)
        # self.means = np.load('./model/means.npy', allow_pickle=True)

        if f: self.pfilename = f
        pfile = open(self.pfilename, 'r')
        self.P = json.load(pfile)
        self.setup_connection()

    def setup_connection(self):
        # == Set Up UDP Socket ==
        try:
            self.so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            print('Error: Could not create socket...')
            sys.exit(-1)
        # == Initialize Connection To Server ==
        self.so.settimeout(1)
        while True:
            # This string establishes track sensor angles! You can customize them.
            # a= "-90 -75 -60 -45 -30 -20 -15 -10 -5 0 5 10 15 20 30 45 60 75 90"
            # xed- Going to try something a bit more aggressive...
            # a= "-36 -32 -28 -24 -20 -16 -12 -8 -4 0 4 8 12 16 20 24 28 32 36"
            # a= "-45 -36 -27.5 -19 -13 -8.4 -4 -1.7 -.5 0 .5 1.7 4 8.4 13 19 27.5 36 45"
            # a= "-45 -27.5 -19 -13 -10 -8.4 -4 -1.7 -.5 0 .5 1.7 4 8.4 10 13 19 27.5 45"
            a = "-90 -75 -50 -35 -20 -15 -10 -5 -1 0 1 5 10 15 20 35 50 75 90"
            # xed- Going to try something a lot more aggressive...
            # a= "-16.699244234 -8.53076560995 -5.7105931375 -4.28915332882 -3.43363036245 -2.86240522611 -2.45403167453 -2.1475854283 -1.909152433 0 1.909152433 2.1475854283 2.45403167453 2.86240522611 3.43363036245 4.28915332882 5.7105931375 8.53076560995 16.699244234"

            initmsg = '%s(init %s)' % (self.sid, a)

            try:
                self.so.sendto(initmsg.encode(), (self.host, self.port))

            except socket.error:  # , emsg:
                sys.exit(-1)
            sockdata = str()
            try:
                sockdata, addr = self.so.recvfrom(1024)
                sockdata = sockdata.decode()
            except socket.error:
                # print "Waiting for server on %d............" % self.port
                pass
            if '***identified***' in sockdata:
                # print "Client connected on %d.............." % self.port
                break

    def parse_the_command_line(self):
        try:
            (opts, args) = getopt.getopt(sys.argv[1:], 'f:H:p:i:m:e:t:s:dhv',
                                         ['host=', 'port=', 'id=', 'steps=',
                                          'episodes=', 'file=', 'track=', 'stage=', 'rounds=',
                                          'debug', 'help', 'version'])
        except getopt.error:
            # print 'getopt error: %s\n%s' % (why, usage)
            sys.exit(-1)
        try:
            for opt in opts:
                if opt[0] == '-h' or opt[0] == '--help':
                    print(usage)
                    sys.exit(0)
                if opt[0] == '-d' or opt[0] == '--debug':
                    self.debug = True
                if opt[0] == '-H' or opt[0] == '--host':
                    self.host = opt[1]
                if opt[0] == '-i' or opt[0] == '--id':
                    self.sid = opt[1]
                if opt[0] == '-t' or opt[0] == '--track':
                    self.trackname = opt[1]
                if opt[0] == '-s' or opt[0] == '--stage':
                    self.stage = int(opt[1])
                if opt[0] == '-p' or opt[0] == '--port':
                    self.port = int(opt[1])
                if opt[0] == '-r' or opt[0] == '--rounds':
                    self.maxRounds = int(opt[1])
                if opt[0] == '-e' or opt[0] == '--episodes':
                    self.maxEpisodes = int(opt[1])
                if opt[0] == '-f' or opt[0] == '--file':
                    self.pfilename = opt[1]
                if opt[0] == '-m' or opt[0] == '--steps':
                    self.maxSteps = int(opt[1])
                if opt[0] == '-v' or opt[0] == '--version':
                    print('%s %s' % (sys.argv[0], version))
                    sys.exit(0)
        except ValueError:  # , why:
            print('Bad parameter \'%s\' for option %s: %s\n%s' % (
                opt[1], opt[0], why, usage))
            sys.exit(-1)
        if len(args) > 0:
            print('Superflous input? %s\n%s' % (', '.join(args), usage))
            sys.exit(-1)

    def get_servers_input(self):
        '''Server's input is stored in a ServerState object'''
        if not self.so: return
        sockdata = str()
        while True:
            try:
                # Receive server data 
                sockdata, addr = self.so.recvfrom(1024)
                sockdata = sockdata.decode()
            except socket.error:  # , emsg:
                print('.')
                # print "Waiting for data on %d.............." % self.port)
            if '***identified***' in sockdata:
                print("Client connected on %d.............." % self.port)
                continue
            elif '***shutdown***' in sockdata:
                print(("Server has stopped the race on %d. " +
                       "You were in %d place.") %
                      (self.port, self.S.d['racePos']))
                self.shutdown()
                return
            elif '***restart***' in sockdata:
                # What do I do here?
                print("Server has restarted the race on %d." % self.port)
                # I haven't actually caught the server doing this.
                self.shutdown()
                return
            elif not sockdata:  # Empty?
                continue  # Try again.
            else:
                self.S.parse_server_str(sockdata)
                if self.debug:
                    sys.stderr.write("\x1b[2J\x1b[H")  # Clear for steady output.
                    print(self.S)
                break  # Can now return from this function.

    def respond_to_server(self):
        if not self.so: return
        try:
            self.so.sendto(repr(self.R).encode(), (self.host, self.port))
        except socket.error:  # , emsg:
            print("Error sending to server: %s Message %s" % (emsg[1], str(emsg[0])))
            sys.exit(-1)
        if self.debug: print(self.R.fancyout())
        # Or use this for plain output:
        # if self.debug: print self.R

    def shutdown(self):
        if not self.so: return
        # print ("Race terminated or %d steps elapsed. Shutting down %d."
        #       % (self.maxSteps,self.port))
        self.so.close()
        self.so = None
        # sys.exit() # No need for this really.


class ServerState():
    '''What the server is reporting right now.'''

    def __init__(self):
        self.servstr = str()
        self.d = dict()

    def parse_server_str(self, server_string):
        '''Parse the server string.'''
        self.servstr = server_string.strip()[:-1]
        sslisted = self.servstr.strip().lstrip('(').rstrip(')').split(')(')
        for i in sslisted:
            w = i.split(' ')
            self.d[w[0]] = destringify(w[1:])

    def __repr__(self):
        # Comment the next line for raw output:
        return self.fancyout()
        # -------------------------------------
        out = str()
        for k in sorted(self.d):
            strout = str(self.d[k])
            if type(self.d[k]) is list:
                strlist = [str(i) for i in self.d[k]]
                strout = ', '.join(strlist)
            out += "%s: %s\n" % (k, strout)
        return out

    def fancyout(self):
        '''Specialty output for useful ServerState monitoring.'''
        out = str()
        sensors = [  # Select the ones you want in the order you want them.
            # 'curLapTime',
            # 'lastLapTime',
            'stucktimer',
            # 'damage',
            # 'focus',
            'fuel',
            # 'gear',
            'distRaced',
            'distFromStart',
            # 'racePos',
            'opponents',
            'wheelSpinVel',
            'z',
            'speedZ',
            'speedY',
            'speedX',
            'targetSpeed',
            'rpm',
            'skid',
            'slip',
            'track',
            'trackPos',
            'angle',
        ]

        # for k in sorted(self.d): # Use this to get all sensors.
        for k in sensors:
            if type(self.d.get(k)) is list:  # Handle list type data.
                if k == 'track':  # Nice display for track sensors.
                    strout = str()
                    #  for tsensor in self.d['track']:
                    #      if   tsensor >180: oc= '|'
                    #      elif tsensor > 80: oc= ';'
                    #      elif tsensor > 60: oc= ','
                    #      elif tsensor > 39: oc= '.'
                    #      #elif tsensor > 13: oc= chr(int(tsensor)+65-13)
                    #      elif tsensor > 13: oc= chr(int(tsensor)+97-13)
                    #      elif tsensor >  3: oc= chr(int(tsensor)+48-3)
                    #      else: oc= '_'
                    #      strout+= oc
                    #  strout= ' -> '+strout[:9] +' ' + strout[9] + ' ' + strout[10:]+' <-'
                    raw_tsens = ['%.1f' % x for x in self.d['track']]
                    strout += ' '.join(raw_tsens[:9]) + '_' + raw_tsens[9] + '_' + ' '.join(raw_tsens[10:])
                elif k == 'opponents':  # Nice display for opponent sensors.
                    strout = str()
                    for osensor in self.d['opponents']:
                        if osensor > 190:
                            oc = '_'
                        elif osensor > 90:
                            oc = '.'
                        elif osensor > 39:
                            oc = chr(int(osensor / 2) + 97 - 19)
                        elif osensor > 13:
                            oc = chr(int(osensor) + 65 - 13)
                        elif osensor > 3:
                            oc = chr(int(osensor) + 48 - 3)
                        else:
                            oc = '?'
                        strout += oc
                    strout = ' -> ' + strout[:18] + ' ' + strout[18:] + ' <-'
                else:
                    strlist = [str(i) for i in self.d[k]]
                    strout = ', '.join(strlist)
            else:  # Not a list type of value.
                if k == 'gear':  # This is redundant now since it's part of RPM.
                    gs = '_._._._._._._._._'
                    p = int(self.d['gear']) * 2 + 2  # Position
                    l = '%d' % self.d['gear']  # Label
                    if l == '-1': l = 'R'
                    if l == '0':  l = 'N'
                    strout = gs[:p] + '(%s)' % l + gs[p + 3:]
                elif k == 'damage':
                    strout = '%6.0f %s' % (self.d[k], bargraph(self.d[k], 0, 10000, 50, '~'))
                elif k == 'fuel':
                    strout = '%6.0f %s' % (self.d[k], bargraph(self.d[k], 0, 100, 50, 'f'))
                elif k == 'speedX':
                    cx = 'X'
                    if self.d[k] < 0: cx = 'R'
                    strout = '%6.1f %s' % (self.d[k], bargraph(self.d[k], -30, 300, 50, cx))
                elif k == 'speedY':  # This gets reversed for display to make sense.
                    strout = '%6.1f %s' % (self.d[k], bargraph(self.d[k] * -1, -25, 25, 50, 'Y'))
                elif k == 'speedZ':
                    strout = '%6.1f %s' % (self.d[k], bargraph(self.d[k], -13, 13, 50, 'Z'))
                elif k == 'z':
                    strout = '%6.3f %s' % (self.d[k], bargraph(self.d[k], .3, .5, 50, 'z'))
                elif k == 'trackPos':  # This gets reversed for display to make sense.
                    cx = '<'
                    if self.d[k] < 0: cx = '>'
                    strout = '%6.3f %s' % (self.d[k], bargraph(self.d[k] * -1, -1, 1, 50, cx))
                elif k == 'stucktimer':
                    if self.d[k]:
                        strout = '%3d %s' % (self.d[k], bargraph(self.d[k], 0, 300, 50, "'"))
                    else:
                        strout = 'Not stuck!'
                elif k == 'rpm':
                    g = self.d['gear']
                    if g < 0:
                        g = 'R'
                    else:
                        g = '%1d' % g
                    strout = bargraph(self.d[k], 0, 10000, 50, g)
                elif k == 'angle':
                    asyms = [
                        "  !  ", ".|'  ", "./'  ", "_.-  ", ".--  ", "..-  ",
                        "---  ", ".__  ", "-._  ", "'-.  ", "'\.  ", "'|.  ",
                        "  |  ", "  .|'", "  ./'", "  .-'", "  _.-", "  __.",
                        "  ---", "  --.", "  -._", "  -..", "  '\.", "  '|."]
                    rad = self.d[k]
                    deg = int(rad * 180 / PI)
                    symno = int(.5 + (rad + PI) / (PI / 12))
                    symno = symno % (len(asyms) - 1)
                    strout = '%5.2f %3d (%s)' % (rad, deg, asyms[symno])
                elif k == 'skid':  # A sensible interpretation of wheel spin.
                    frontwheelradpersec = self.d['wheelSpinVel'][0]
                    skid = 0
                    if frontwheelradpersec:
                        skid = .5555555555 * self.d['speedX'] / frontwheelradpersec - .66124
                    strout = bargraph(skid, -.05, .4, 50, '*')
                elif k == 'slip':  # A sensible interpretation of wheel spin.
                    frontwheelradpersec = self.d['wheelSpinVel'][0]
                    slip = 0
                    if frontwheelradpersec:
                        slip = ((self.d['wheelSpinVel'][2] + self.d['wheelSpinVel'][3]) -
                                (self.d['wheelSpinVel'][0] + self.d['wheelSpinVel'][1]))
                    strout = bargraph(slip, -5, 150, 50, '@')
                else:
                    strout = str(self.d[k])
            out += "%s: %s\n" % (k, strout)
        return out


class DriverAction():
    '''What the driver is intending to do (i.e. send to the server).
    Composes something like this for the server:
    (accel 1)(brake 0)(gear 1)(steer 0)(clutch 0)(focus 0)(meta 0) or
    (accel 1)(brake 0)(gear 1)(steer 0)(clutch 0)(focus -90 -45 0 45 90)(meta 0)'''

    def __init__(self):
        self.actionstr = str()
        # "d" is for data dictionary.
        self.d = {'accel': 0.2,
                  'brake': 0,
                  'clutch': 0,
                  'gear': 1,
                  'steer': 0,
                  'focus': [-90, -45, 0, 45, 90],
                  'meta': 0
                  }

    def clip_to_limits(self):
        """There pretty much is never a reason to send the server
        something like (steer 9483.323). This comes up all the time
        and it's probably just more sensible to always clip it than to
        worry about when to. The "clip" command is still a snakeoil
        utility function, but it should be used only for non standard
        things or non obvious limits (limit the steering to the left,
        for example). For normal limits, simply don't worry about it."""
        self.d['steer'] = clip(self.d['steer'], -1, 1)
        self.d['brake'] = clip(self.d['brake'], 0, 1)
        self.d['accel'] = clip(self.d['accel'], 0, 1)
        self.d['clutch'] = clip(self.d['clutch'], 0, 1)
        if self.d['gear'] not in [-1, 0, 1, 2, 3, 4, 5, 6]:
            self.d['gear'] = 0
        if self.d['meta'] not in [0, 1]:
            self.d['meta'] = 0
        if type(self.d['focus']) is not list or min(self.d['focus']) < -180 or max(self.d['focus']) > 180:
            self.d['focus'] = 0

    def __repr__(self):
        self.clip_to_limits()
        out = str()
        for k in self.d:
            out += '(' + k + ' '
            v = self.d[k]
            if not type(v) is list:
                out += '%.3f' % v
            else:
                out += ' '.join([str(x) for x in v])
            out += ')'
        return out
        return out + '\n'

    def fancyout(self):
        '''Specialty output for useful monitoring of bot's effectors.'''
        out = str()
        od = self.d.copy()
        od.pop('gear', '')  # Not interesting.
        od.pop('meta', '')  # Not interesting.
        od.pop('focus', '')  # Not interesting. Yet.
        for k in sorted(od):
            if k == 'clutch' or k == 'brake' or k == 'accel':
                strout = ''
                strout = '%6.3f %s' % (od[k], bargraph(od[k], 0, 1, 50, k[0].upper()))
            elif k == 'steer':  # Reverse the graph to make sense.
                strout = '%6.3f %s' % (od[k], bargraph(od[k] * -1, -1, 1, 50, 'S'))
            else:
                strout = str(od[k])
            out += "%s: %s\n" % (k, strout)
        return out


# == Misc Utility Functions
def destringify(s):
    '''makes a string into a value or a list of strings into a list of
    values (if possible)'''
    if not s: return s
    if type(s) is str:
        try:
            return float(s)
        except ValueError:
            print("Could not find a value in %s" % s)
            return s
    elif type(s) is list:
        if len(s) < 2:
            return destringify(s[0])
        else:
            return [destringify(i) for i in s]


def drive_example(c):
    S, R = c.S.d, c.R.d
    target_speed = 50

    # Steer To Corner
    R['steer'] = S['angle'] * 10 / PI
    # Steer To Center
    R['steer'] -= S['trackPos'] * .10

    # Throttle Control
    if S['speedX'] < target_speed - (R['steer'] * 50):
        R['accel'] += 10
    else:
        R['accel'] -= .01
    if S['speedX'] < 10:
        R['accel'] += 1 / (S['speedX'] + .1)

    # Traction Control System
    if ((S['wheelSpinVel'][2] + S['wheelSpinVel'][3]) -
            (S['wheelSpinVel'][0] + S['wheelSpinVel'][1]) > 5):
        R['accel'] -= .2

    # Automatic Transmission
    R['gear'] = 1
    if S['speedX'] > 50:
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

    # data_tuple_angle = tuple(data_dict_angle)
    # data_dict_angle.append(data_tuple_angle)
    data_dict_angle.append(S['angle'])
    data_dict_speed.append(S['speedX'])
    data_dict_track.append(S['track'])
    data_dict_steer.append(R['steer'])
    data_dict_accel.append(R['accel'])
    data_dict_break.append(R['brake'])

    # print every 50 steps the focus sensor
    if c.maxSteps % 50 == 0:
        if S['focus'][0] != -1:
            print("focus: ", S['focus'])
        else:
            print("!!!")


    if S['trackPos'] < 0.5 or S['trackPos'] < -0.5:
        R['break'] = 1
    else:
        R['break'] = 0
    return


def own_driver(c):
    S, R = c.S.d, c.R.d
    target_speed = 100
    if S['speedX'] < target_speed:
        R['accel'] += 5
    else:
        R['accel'] -= 1
    
    if S['angle'] > 10:
        R['break'] = 1
    return

def write_csv_file(dict_angle, dict_speed, dict_track, dict_steer, dict_accel, dict_break):
# def write_csv_file(dict_angle, dict_speed, dict_track, dict_steer, dict_accel):
    print("write csv file")
    csv_columns = ['angle', 'speed', 'track', 'steer', 'accel', 'break']
    with open('data.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(csv_columns)
        # data = list(zip(dict_angle, dict_speed, dict_track, dict_steer))
        data = list(zip(dict_angle, dict_speed, dict_track, dict_steer, dict_accel, dict_break))
        # data = list(zip(dict_angle, dict_speed, dict_track, dict_steer, dict_accel))
        for row in data:
            row = list(row)
            writer.writerow(row)
        

if __name__ == "__main__":
    print("===============================================")
    C = Client()
    count = 0
    for step in range(C.maxSteps, 0, -1):
        C.get_servers_input()
        if step % 3 == 0:
            drive_example(C)
            # own_driver(C) 
            C.respond_to_server()
    C.shutdown()
    print("Track name:  ", C.S.d['track'])
    print("data_dict_track: ")
    # print(data_dict_track)
    print(data_dict_track[40])
    # for i in data_dict_angle:
    #     print(i)
    print("===============================================")
    write_csv_file(data_dict_angle, data_dict_speed, data_dict_track, data_dict_steer, data_dict_accel, data_dict_break)
    # write_csv_file(data_dict_angle, data_dict_speed, data_dict_track, data_dict_steer, data_dict_accel)