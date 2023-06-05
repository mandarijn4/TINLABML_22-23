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


with open('aalborg_3laps.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)

kiwi = data
# add track as list
kiwi[1] = kiwi[1] + list(kiwi[1][3].replace("[", "").replace("]", "").replace("\"", " ").split(", "))
del (kiwi[1][3]) # remove string track
del (kiwi[1][0]) # remove laptime
cherry = np.array(kiwi[1]) # load to numpy array
banana = cherry.astype(float) # convert str to floats
pear = list(banana) # make list

print(Data.ANGLE.value)
print(pear[Data.ANGLE.value])