# Title: Dali Bus Test
#  _____          _      _____   ____              _______        _
# |  __ \   /\   | |    |_   _| |  _ \            |__   __|      | |
# | |  | | /  \  | |      | |   | |_) |_   _ ___     | | ___  ___| |_
# | |  | |/ /\ \ | |      | |   |  _ <| | | / __|    | |/ _ \/ __| __|
# | |__| / ____ \| |____ _| |_  | |_) | |_| \__ \    | |  __/\__ \ |_
# |_____/_/    \_\______|_____| |____/ \__,_|___/    |_|\___||___/\__|
#
#
# Author: Joshua Bijak
# Date:  14/05/2019
# Desc:  Test for daliBus Class
# Changelog: 14/05/2019 -  Initial Log.
#            Initialization of Test

import serial
import sys
import os
import time

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

import dali_hat.daliBus as daliBus


# Initialize the Port Using Defaults
daliTestBus = daliBus.DaliBus()
# Query the Bus
daliTestBus.dali_querybus()
# Query the Version
daliTestBus.dali_version()
# Send All Off
daliTestBus.dali_send_16_cmd("FE", "00", 0)
time.sleep(1)
# Send All On
daliTestBus.dali_send_16_cmd("FE", "FE", 0)
time.sleep(1)
# Send All Off
daliTestBus.dali_send_16_cmd("FE", "00", 0)
time.sleep(1)
# Test Initialization
daliTestBus.dali_init()


