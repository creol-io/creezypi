import serial
import sys
import os
import time

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))


import dali_hat.daliCommands as daliCommands

"""
Initialize the BUS w extended commands
"""
print("Initializing the BUS with commands")
daliGroupTestBus = daliCommands.daliCommands()
print("Complete")

for i in range(16):
    print("Group " +str(i)+"Off")
    daliGroupTestBus.controlgroup(i, 0)
    time.sleep(2)
    print("Group " + str(i) + "On")
    daliGroupTestBus.controlgroup(i, 254)
    time.sleep(2)
    print("Group " + str(i) + "Off")
    daliGroupTestBus.controlgroup(i, 0)
    time.sleep(2)