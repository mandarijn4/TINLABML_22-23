import socket
import json
import sys
import getopt
from driver import DriverAction
from server import ServerState

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
