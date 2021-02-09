# Title: Dali Bus
#	  _____          _      _____   ____
#	 |  __ \   /\   | |    |_   _| |  _ \
#	 | |  | | /  \  | |      | |   | |_) |_   _ ___
#	 | |  | |/ /\ \ | |      | |   |  _ <| | | / __|
#	 | |__| / ____ \| |____ _| |_  | |_) | |_| \__ \
#	 |_____/_/    \_\______|_____| |____/ \__,_|___/
#
# Author: Joshua Bijak
# Date:  07/05/2019
# Desc:  Interface for Talking to DALI-HAT via DALI
# Changelog: 07/05/2019 -  Initial Log.
#            Initialization of Class and Connection. Generic Commands Listed as funcs
#            14/05/2019 - Initialization Complete

import serial
import sys
import RPi.GPIO as GPIO
import time
import math


class DaliBus:

    # Open Serial Connection on DALI Hat
    daliSerial = 0
    defaultPORT = '/dev/ttyS0'
    defaultBAUD = 19200
    defaultPARITY = serial.PARITY_NONE
    defaultSTOP = serial.STOPBITS_ONE
    defaultBYTE = serial.EIGHTBITS
    defaultTIMEOUT = 1
    # Coms Timing Delay in ms
    delaytime = 0.5
    bufferclean = 1

    daliRESET = '20'
    daliINIT = 'A5'
    daliQUERY = '90'
    daliQUERYSHORTADDR= 'BB'
    daliRNDM = 'A7'
    daliBROADCAST_DP = 'FE'
    daliBROADCAST_C = 'FF'
    daliOFF = '00'
    daliON = 'FE'
    daliTERM = 'A1'
    daliWITHDRAWA = 'AB'
    daliWITHDRAWB = '00'
    daliWRITESHORT = 'B7'
    daliSEARCHHB = 'B1'
    daliSEARCHMB = 'B3'
    daliSEARCHLB = 'B5'
    daliCOMPARE = 'A9'
    max_attempts = 10

    def __init__(self, port=defaultPORT, baudrate=defaultBAUD, parity=defaultPARITY, stopbits=defaultSTOP,
                 bytesize=defaultBYTE, timeout=defaultTIMEOUT):
            print("Initializing Using this Config: \n")
            print('Port: '+str(port)+'\n')
            print('Baud: ' + str(baudrate) + '\n')
            print('Parity: ' + str(parity) + '\n')
            print('Stop Bits: ' + str(stopbits) + '\n')
            print('Bytesize: '+str(bytesize)+'\n')
            print('Timeout: ' + str(timeout) + '\n')

            self.daliSerial = serial.Serial(port, baudrate, bytesize, parity, stopbits, timeout)

    def dali_init(self):
        # Send Terminate Command to Kill Old Sessions
        self.dali_send_16_cmd(self.daliTERM, self.daliOFF, False)
        time.sleep(self.delaytime)
        # Send Reset Command Twice
        print('Resetting Bus...')
        self.dali_send_16_twice_cmd(self.daliBROADCAST_C, self.daliRESET, False)
        time.sleep(self.delaytime)
        print('Complete \n')
        # Send OFF
        self.dali_send_16_cmd(self.daliBROADCAST_C, self.daliOFF, False)
        time.sleep(self.delaytime)
        # Send Initialise Command Twice
        print('Initialising Bus...')
        self.dali_send_16_twice_cmd(self.daliINIT, self.daliOFF, False)
        time.sleep(self.delaytime)
        print('Complete \n')
        # Send Randomize Command Twice
        print('Randomizing Addresses...')
        self.dali_send_16_twice_cmd(self.daliRNDM, self.daliOFF, False)
        time.sleep(self.delaytime)
        print('Complete \n')

        print('Beginning Assigning of Addresses... \n')
        time.sleep(self.delaytime)
        self.dali_search_and_assign_address_v4()

        # Send Terminate Command
        self.dali_send_16_cmd(self.daliTERM, self.daliOFF, False)
        time.sleep(self.delaytime)
        print('Beginning Search Address...\n')
        self.dali_search_address()

        print("Initialization Complete")

    def dali_search_address(self):

        index = 0
        while index < 64:
            # Clean Buffer First
            x = self.daliSerial.read(100)
            # Convert to Individual Address  (2* BitShift 1)
            a = (index * 2) + 1
            # Query  Actual Dim Level
            self.daliSerial.write(('h%02XA0\n' % a).encode())
            # Read Response
            x = self.daliSerial.read(1).decode()
            # Expected Answer if address is real is 'J'
            if x == 'J':
                # Read Light Level
                x = self.daliSerial.read(2).decode()
                y = x
                # Clean CRLF Chars
                x = self.daliSerial.read(1).decode()
                # Read Model (if Any)
                self.daliSerial.write(('h%02XA6\n' % a).encode())
                x = self.daliSerial.read(1).decode()
                z = "  "
                if x == 'J':
                    z = self.daliSerial.read(2).decode()
                # Clean CRLF Chars
                x = self.daliSerial.read(1).decode()
                # Read LED Type
                self.daliSerial.write(('h%02X99\n' % a).encode())
                x = self.daliSerial.read(1).decode()
                dt = "  "
                if x == 'J':
                    dt = self.daliSerial.read(2)
                # Clean CRLF Chars
                x = self.daliSerial.read(1)
                print('Address Found! At: ' + str(index) + ' it is Model ' + str(z) + 'Driver Type is: ' + str(dt) + ' Level is ' + str(y))
            else:
                x = self.daliSerial.read(1)
            index = index + 1

    def dali_search_and_assign_address_v4(self):
        """
        High Speed-Ultra Slim Initialization v2

        :return:
        """
        # terminate DALI
        print("             Terminating...")
        self.daliSerial.write(("hA100\n").encode())
        print(self.dali_read_bytes())
        # Reset DALI
        print("             Resetting...")
        self.daliSerial.write(("tFF20\n").encode())
        print(self.dali_read_bytes())

        # Enable Search mode
        print("             Enabling search...")
        self.daliSerial.write(("tA500\n").encode())
        print(self.dali_read_bytes())
        # Random Address
        print("             Randomizing")
        self.daliSerial.write(("tA700\n").encode())
        print(self.dali_read_bytes())

        topByte = 256
        lowByte = 0
        searchByte = (topByte + lowByte) / 2

        searchComplete = False
        highsearch = False
        midsearch = False
        lowsearch = False

        searchmatchlow = 0
        searchmatchmid = 0
        searchmatchhigh = 0

        short_address = 0

        low_longadd = int("0x000000", 16)
        high_longadd = int("0xFFFFFF", 16)
        longadd = (high_longadd + low_longadd) / 2
        longadd = int(longadd)
        highbyte = int("0x0", 16)
        middlebyte = int("0x0", 16)
        lowbyte = int("0x0", 16)
        short_address = int("0x0", 16)

        # Search Loop

        while longadd <= int("0xFFFFFF", 16)-2 and short_address <= 64:
            while high_longadd-low_longadd > 1:
                # Assign the search bytes for looking
                shift_long = hex(longadd)
                highbyte = shift_long[2:4]
                middlebyte = shift_long[4:6]
                lowbyte = shift_long[6:8]

                self.daliSerial.write(("hB1" + highbyte + "\n").encode())
                print(self.dali_read_bytes())
                self.daliSerial.write(("hB3" + middlebyte + "\n").encode())
                print(self.dali_read_bytes())
                self.daliSerial.write(("hB5" + lowbyte + "\n").encode())
                print(self.dali_read_bytes())
                rsp = "D"
                # D signifies Bus power failure. Too far for comms etc.
                attempts = 0
                while rsp[0] == "D" or attempts > 3:
                    self.daliSerial.write(("hA900\n").encode())
                    rsp = self.dali_read_bytes()
                    attempts = attempts +1

                if rsp[0] == 'J' or rsp[0] == 'X':
                    high_longadd = longadd
                    print("Response Answered: New HighLong: "+str(high_longadd))
                else:
                    low_longadd = longadd
                    print("No Response: New LowLong: " + str(low_longadd))
                # Check new search params
                longadd = (low_longadd + high_longadd)/2
                longadd = int(longadd)
                # Print Current Search ADdress
                print('BIN: ' + str(bin(longadd)) + " " + 'DEC: ' + str(int(longadd)) + " " + 'HEX: ' + str(hex(longadd)) + "\n")

            if high_longadd != int("0xFFFFFF", 16):
                print("Address Found!")
                # Assign the search bytes for looking

                shift_long = hex(longadd + 1)
                highbyte = shift_long[2:4]
                middlebyte = shift_long[4:6]
                lowbyte = shift_long[6:8]

                # Search bytes
                # Convert int to hex string again

                self.daliSerial.write(("hB1"+highbyte+"\n").encode())
                print(self.dali_read_bytes())
                self.daliSerial.write(("hB3" + middlebyte + "\n").encode())
                print(self.dali_read_bytes())
                self.daliSerial.write(("hB5" + lowbyte + "\n").encode())
                print(self.dali_read_bytes())

                # Program Search Address
                # Bit shift the address
                short_program = 1 + (short_address << 1)
                direct_short = (short_address << 1)
                short_program = '{0:0{1}X}'.format(short_program, 2)
                direct_short = '{0:0{1}X}'.format(direct_short, 2)
                print("Assiging Short Address :" + str(short_address) + " bitshifted: " + short_program + "\n")

                self.daliSerial.write(("hB7" + str(short_program) + "\n").encode())
                print(self.dali_read_bytes())

                short_address = short_address + 1

                print("             Querying....")
                # # Query short address
                self.daliSerial.write(("hBB00\n").encode())
                print(self.dali_read_bytes())
                #print("             Setting DTR1...")
                # # Set DTR (DTR = 11)
                #self.daliSerial.write(("hA30B\n").encode())
                #print(self.dali_read_bytes())
                # # Set DTR1 (DTR1 = 0)
                #self.daliSerial.write(("hC300\n").encode())
                #print(self.dali_read_bytes())
                # Withdraw
                print("          Withdrawing...")
                self.daliSerial.write(("tAB00\n").encode())
                print(self.dali_read_bytes())

                print("          Testing On/Off...")
                self.daliSerial.write(("h" + str(short_program) + "FF\n").encode())
                print(self.dali_read_bytes())
                self.daliSerial.write(("h" + str(short_program) + "00\n").encode())
                print(self.dali_read_bytes())

                # Reset the entire search
                high_longadd = int("0xFFFFFF", 16)

                longadd = (low_longadd + high_longadd) / 2
                longadd = int(longadd)

    def dali_search_byte(self, byte):
        # Compare the answer, and wait for confirm
        response = str()
        debug_search_byte = True

        # Reassign the search params
        topByte = 255
        bottomByte = 0

        daliSearchByteCMD = 0
        searchByte = (topByte+bottomByte)/2
        searchByte = int(searchByte)
        prevByte = int(searchByte)
        if byte =="HIGH":
            daliSearchByteCMD = self.daliSEARCHHB
        elif byte =="MID":
            daliSearchByteCMD = self.daliSEARCHMB
        elif byte == "LOW":
            daliSearchByteCMD = self.daliSEARCHLB
        else:
            print("Error in Search byte parameter")
            return

        while topByte - bottomByte > 1:
            # Send current search byte
            hexByte = '{0:0{1}X}'.format(searchByte, 2)
            if debug_search_byte:
                print("Current search byte: "+ hexByte)

            self.dali_send_16_cmd(daliSearchByteCMD, hexByte, False)
            time.sleep(self.delaytime)
            response = self.dali_send_16_cmd(self.daliCOMPARE, self.daliOFF, True)
            # TODO: Fix rounding error here
            if response[0] == 'J' or response[0] == 'X':
                topByte = searchByte
                searchByte = math.ceil((topByte + bottomByte)/2)
                searchByte = int(searchByte)

            else:
                bottomByte = searchByte
                searchByte = math.ceil((topByte + bottomByte)/2)
                searchByte = int(searchByte)
        print("Final Search Byte: "+'{0:0{1}X}'.format(searchByte, 2))
        print("Final Bottom Byte: "+'{0:0{1}X}'.format(bottomByte, 2))
        print("Final Top Byte: "+'{0:0{1}X}'.format(topByte, 2))
        return topByte

    def dali_read_bytes(self):
        time.sleep(self.delaytime)
        received = False
        while not received:
            bytestoread = self.daliSerial.in_waiting
            rsp = self.daliSerial.read(bytestoread)
            # print(rsp)
            searchrsp = str(rsp)
            Jres = searchrsp.find("J")
            Xres = searchrsp.find("X")
            Dres = searchrsp.find("D")
            if Jres != -1:
                rsp = searchrsp[Jres:Jres+3]
            elif Xres != -1:
                rsp = "X"
            elif Dres != -1:
                rsp = "D"
            else:
                rsp = "N"
            received = True
            return rsp

    def dali_send_8_cmd(self, command_hex, confirm):
        # Clean Buffer
        attempts = 0
        response = 0
        cmd = ('j' + command_hex + "\n").encode()
        # If we are waiting for specfic response then repeat otherwise fire and forget
        if confirm is not True:
            self.daliSerial.write(cmd)
            response = self.dali_receive()
            response = 'N'
            return response
        while attempts < self.max_attempts:
            self.daliSerial.readline()
            self.daliSerial.write(cmd)
            response = self.dali_receive()
            if response[0] == 'J' or response == 'H' or response == 'L' or response == 'N':
                print("Attempts: " + str(attempts))
                attempts = self.max_attempts
            attempts += 1

        return response

    def dali_send_16_twice_cmd(self, dest_hex, command_hex, confirm):
        # Clean Buffer
        attempts = 0
        response = 0

        cmd = ('t' + dest_hex + command_hex + "\n")

        if confirm is not True:
            self.daliSerial.read(self.bufferclean)
            self.daliSerial.write(cmd.encode())
            response = 'N'
            return response
        while attempts < self.max_attempts:
            self.daliSerial.read(self.bufferclean)
            self.daliSerial.write(cmd.encode())
            response = self.dali_receive()
            if response[0] == 'J' or response == 'H' or response == 'L' or response == 'N':
                print("Attempts: " + str(attempts))
                attempts = self.max_attempts
            attempts += 1

        return response

    def dali_send_16_cmd(self, dest_hex, command_hex, confirm):
        # Clean Buffer
        attempts = 0
        total_response = 'N'
        cmd = ('h' + dest_hex + command_hex + "\n")
        if confirm:
            while attempts < self.max_attempts:
                print("Yes Confirm... beginning attempt: " + str(attempts) + " of " + str(self.max_attempts))
                self.daliSerial.read(self.bufferclean)
                self.daliSerial.write(cmd.encode())
                response = self.daliSerial.read(1).decode()
                # TODO: Account for L and H cases
                if response == 'J' or response == 'H' or response == 'L' or response == 'N' or response == 'X':
                    attempts = attempts + 1
                    print("Attempts: " + str(attempts))
                    if response == 'J':
                        response_rest = self.daliSerial.read(2).decode()
                        print("Full Response: " + response + response_rest)
                        full_resp = response + response_rest
                        total_response = full_resp
                        break
                    if response == 'N':
                        print("No Response")
                        attempts = self.max_attempts
                        total_response = response
                        break
                    if response == 'X':
                        print("Framing Error: Moving to next...")
                        total_response = 'X'
                        break
                #elif response == 'X':
                #    print("Framing error")
                attempts += 1
            print("Response final: " + total_response)
            return total_response
        else:
            # print("No confirm... Firing and Forgetting")
            self.daliSerial.write(cmd.encode())
            # self.daliSerial.read(self.bufferclean)
            return total_response

    def dali_send_24_cmd(self, byte1, dest_hex, command_hex, confirm):
        # Clean Buffer
        attempts = 0
        response = 0
        cmd = ('l'+byte1+dest_hex+command_hex+"\n").encode()
        if confirm is not True:
            self.daliSerial.write(cmd)
            response = 'N'
            return response
        while attempts < self.max_attempts:
            self.daliSerial.write(cmd)
            response = self.dali_receive()
            if response[0] == 'J' or response == 'H' or response == 'L' or response == 'N':
                break
            # If we are waiting for specfic response then repeat otherwise exit
            if confirm is not True:
                break

        return response

    def dali_receive(self):
        response = self.daliSerial.read(1).decode()
        if response == 'J':
            # 1 Byte Response
            complete_val = response + self.daliSerial.read(2).decode()
            print("Received: "+str(complete_val))
            return complete_val
        elif response == 'H':
            # 2 Byte Response
            complete_val = response + self.daliSerial.read(4).decode()
            return complete_val
        elif response == 'L':
            # 3 Byte Response
            complete_val = response + self.daliSerial.read(6).decode()
            return complete_val
        elif response == 'N':
            # No Response Clean Buffer
            response = 'N'
            return response
        elif response == 'X':
            return response
        elif response == 'D':
            return response
        else:
            response = 'X'
            return response

    def dali_querybus(self):

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(5, GPIO.IN)
        GPIO.setup(6, GPIO.IN)

        print('\n      Creol - Creezy Pi     \n')
        print('\n      Bus Query     \n')
        if GPIO.input(6) == 0:
            print('Power: Primary Power missing')
        else:
            print('Power: Primary Power OK')

        if GPIO.input(5) == 0:
            print('Power: Secondary Power missing')
        else:
            print('Power: Secondary Power OK')
        self.daliSerial.write('d\n'.encode())  # now check if Power is good
        x = self.daliSerial.read(1).decode()
        if x == 'D':
            y = self.daliSerial.read(2).decode()
            y = int(y, 16)
            if y == 0:
                print('DALI BUS: power is lost')
            if y == 1:
                print('DALI BUS: power is stuck high')
            if y == 2:
                print('DALI BUS: power is good')
            if y == 3:
                print('DALI BUS: power is not yet known')
        print(' ')

    def dali_version(self):
        print('\n      Creol - Creezy Pi     \n')
        print('\n      Version Query    \n')
        self.daliSerial.write('v\n'.encode())  # lets get version number first
        x = self.daliSerial.read().decode()
        if x == "":
            print(' Missing Firmware \n')
        else:
            x = self.daliSerial.read(2).decode()
            print('HW version: ' + x)
            y = self.daliSerial.read(2).decode()
            print('FW version: ' + y)
            y = self.daliSerial.read(1)
