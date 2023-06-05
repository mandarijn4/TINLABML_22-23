import csv
import numpy as np
from enum import Enum

class Data(Enum):
    ANGLE = 0
    SPEED = 1
    STEER = 2
    ACCEL = 3
    BRAKE = 4
    TRACK = 5
    TRACK_AMOUNT = 19

class DataFile():
    file = None
    file_as_list = []

    input_ranges = [[-np.pi, np.pi], [-200, 200], [-1, 1], [0,1], [0,1], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200], [0,200]]

    def loadFile(self):
        with open('aalborg_3laps.csv', newline='') as f:
            reader = csv.reader(f)
            self.file = list(reader)

        for i in range(1, len(self.file)):
            file = self.file
            file[i] = file[i] + list(file[i][3].replace("[", "").replace("]", "").replace("\"", " ").split(", "))
            del (file[i][3]) # remove string track
            del (file[i][0]) # remove laptime
            row_as_np_str = np.array(file[i]) # load to numpy array
            row_as_np_float = row_as_np_str.astype(float) # convert str to floats
            row_as_list = list(row_as_np_float) # make list
            # add row to list
            self.file_as_list.append(row_as_list)

data = DataFile()

data.loadFile()

print(data.file_as_list[30000])

    



# kiwi = data
# # add track as list
# kiwi[1] = kiwi[1] + list(kiwi[1][3].replace("[", "").replace("]", "").replace("\"", " ").split(", "))
# del (kiwi[1][3]) # remove string track
# del (kiwi[1][0]) # remove laptime
# cherry = np.array(kiwi[1]) # load to numpy array
# banana = cherry.astype(float) # convert str to floats
# pear = list(banana) # make list



# print(Data.ANGLE.value)
# print(pear[Data.ANGLE.value])