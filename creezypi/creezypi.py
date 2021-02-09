# Title: CreezyPi
#   _____                         _____ _
#  / ____|                       |  __ (_)
# | |     _ __ ___  ___ _____   _| |__) |
# | |    | '__/ _ \/ _ \_  / | | |  ___/ |
# | |____| | |  __/  __// /| |_| | |   | |
#  \_____|_|  \___|\___/___|\__, |_|   |_|
#                            __/ |
#                          |___/
#
#
#
# Author: Joshua Bijak
# Date:  18/06/2019
# Desc:  CreezyPi Class
# Changelog: 18/06/2019 -  Initial Log.
#            Initialization of Main script
import json
import sys
import os
import time
import asyncio

from pywallet import wallet

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

dali_enable = True
debug = True
stateMonitor_Enable = True
pending_flag = False
coap_flag = False
offset_flag = False
offset_frequency_s = 3600
country_code = 'GB'
LED_Group_ID = 'CP1'
VCUIndexes = [123, 124, 125, 126, 127]

LEDLoopTimer = 0.1

"""
Dummy Owner for now.
"""
VCUOwner = '0x44515119087cb5A19DdCA3e909ff6537C23f9Ca8'

# TODO: Each creezypi to generate own keys and then be added by the commissioner
creezyPhrase = 'MNEMONIC_PHRASE_HERE'

creezyPrivKey = 'PRIVATE_KEY_FOR_PI_HERE'
creezyPiAddress = 'PUBLIC_ADDRESS_HERE'

if dali_enable:
    import dali_hat.daliBus as daliBus
if stateMonitor_Enable:
    import eth.statemonitor as stateMonitor

print("Initializing CreezyPi v0.1....")
daliCreezy = None
roomState = None

roomStateAddress = 0

# This current Creezy Coap Address
creezyCoapAddr = 0
# Lookup index for this Creezy
coapAddrIndex = 0
# Other coap addresses in this room
roomCoapAddresses = list()
numCreezies = int()
ledStateAbi = object()
LEDStates = list()

from daliserver import daliserver as daliserver


# creezy_filters = None
# LED_State_Filters = None


def load_modules():
    """
	Loads the DALI Bus and initializes the serial connection to the ATX LED hat
	Also loads the Statemonitor module to start watching a set of contracts.
	:return: No return
	"""
    print("Modules loading....")
    global roomState
    global daliCreezy
    daliCreezy = daliBus.DaliBus()
    roomState = stateMonitor.StateMonitor(defaultWeb3Account=VCUOwner)


def load_contract_abis():
    """
	Pull the contract ABIs from the deployed Truffle JSON packages. Currently assumes some default deployments,
	TODO: Allow for dynamic ABI deployment and even contract deployment in commissioning phase
	:return:
	"""
    # Pull Room Contract Data from Truffle
    global roomStateAddress
    global roomState
    global LEDStates
    global ledStateAbi
    global creezy_leader

    dirname = os.path.dirname(__file__)
    RoomStateFile = os.path.join(dirname, '../creol-eth/build/contracts/RoomState.json')

    # with open("./creol-creezypi/creol-eth/contracts/build/contracts/RoomState.json") as RoomStateContractFile:
    with open(RoomStateFile) as RoomStateContractFile:

        # Load File
        roomData = json.load(RoomStateContractFile)

        if roomData['abi'] != {}:
            print("Network Deployment Detected...")
            # TODO: Check for dynamic network deteciton (Mainnet vs. Testnet)
            # TODO: Check address based on site lookup for now it is hardcoded
            print("Using contract at 0x12EaC4f25E50f992c462f1404c950e304E61d70D")

            roomStateAddress = "0x12EaC4f25E50f992c462f1404c950e304E61d70D"
            roomState = stateMonitor.StateMonitor(defaultWeb3Account=VCUOwner)
            roomState.init_room_state()

            # TODO: Make this dynamic and pull from contract at creezie number 1
            # Currently Assume that there is always a "Creezy-Leader" Deployed
            creezy_leader = "Site-3-Room-2-Creezy-1"

            roomState.connect_room_state(roomStateAddress, creezy_leader)

        else:
            print("No Deployment for this room... please check that you have deployed a RoomState Contract")
            exit(1)

    # with open("./creol-creezypi/creol-eth/contracts/build/contracts/LEDState.json") as LEDStateContractFile:
    LEDStateFile = os.path.join(dirname, "../creol-eth/build/contracts/LEDState.json")
    with open(LEDStateFile) as LEDStateContractFile:
        LEDData = json.load(LEDStateContractFile)
        ledStateAbi = LEDData['abi']
        LEDStates = list()
        for i in roomState.LEDAddresses:
            LEDStates.append(roomState.web3.eth.contract(address=i, abi=ledStateAbi))
        print("LED States Loaded")


def handle_dali_enable():
    """
	Handles the initialization of the DALI Bus
	:return: No return
	"""
    if dali_enable:
        print("Initializing DALI...")
        global daliCreezy
        daliCreezy = daliBus.DaliBus()
        if debug:
            # Query the Bus
            daliCreezy.dali_querybus()
            # Query the Version
            daliCreezy.dali_version()
            # Send All Off
            daliCreezy.dali_send_16_cmd("FE", "FE", 0)
            time.sleep(1)
            # Send All On
            daliCreezy.dali_send_16_cmd("08", "A5", 0)
        time.sleep(1)
        # TODO: Actually check the DALI bus is alive.
        print("DALI Passed...Light Check Ok")


def handle_new_led_state(event):
    global roomState
    if debug:
        print("New LED State Found: ", event.args.updatedState)
    if dali_enable:
        # Fetch a temporary contract instance
        tempContractCall = roomState.web3.eth.contract(address=event.address, abi=ledStateAbi)

        # Get DALI Short Address
        daliShort = tempContractCall.functions.getDALIShortAddress().call()

        # convert to direct command
        direct_short = (daliShort << 1)
        direct_short = '{0:0{1}X}'.format(direct_short, 2)
        print(direct_short)
        # Send State Command To the LED
        if event.args.updatedState:
            dimSet = tempContractCall.functions.getDim().call()
            print(dimSet)
            dimSet = '{:02X}'.format(dimSet)
            print(dimSet)
            daliCreezy.dali_send_16_cmd(str(direct_short), str(dimSet), 0)
        else:
            daliCreezy.dali_send_16_cmd(str(direct_short), daliCreezy.daliOFF, 0)


def handle_new_led_dim(event):
    global roomState
    if debug:
        print("New LED Dim Found: ", event.args.LEDDim)
    if dali_enable:
        # Fetch a temporary contract instance
        tempContractCall = roomState.web3.eth.contract(address=event.address, abi=ledStateAbi)

        # Get DALI Short Address
        daliShort = tempContractCall.functions.getDALIShortAddress().call()
        # Check that DLT says its supposed to be on too
        daliState = tempContractCall.functions.getState().call()
        # convert to direct command
        direct_short = (daliShort << 1)
        direct_short = '{0:0{1}X}'.format(direct_short, 2)
        print(direct_short)
        # Send State Command To the LED
        if daliState:
            dimSet = tempContractCall.functions.getDim().call()
            print(dimSet)
            dimSet = '{:02X}'.format(dimSet)
            print(dimSet)
            daliCreezy.dali_send_16_cmd(str(direct_short), str(dimSet), 0)
        # TODO: Set DALI dimming in driver via DTR
        else:
            daliCreezy.dali_send_16_cmd(str(direct_short), daliCreezy.daliOFF, 0)


async def led_state_log_loop(event_filters, poll_interval):
    while True:

        # if roomState.check_web3_connection():
        if True:
            for curEventFilter in event_filters:
                for event in curEventFilter.get_new_entries():
                    handle_new_led_state(event)
        await asyncio.sleep(poll_interval)


async def led_dim_log_loop(event_filters, poll_interval):
    while True:
        # if roomState.check_web3_connection():
        if True:
            for curEventFilter in event_filters:
                for event in curEventFilter.get_new_entries():
                    handle_new_led_dim(event)
        await asyncio.sleep(poll_interval)


def handle_new_creezy_state(event):
    if debug:
        print("New Creezy in Room, new num of creezies: ", event.args.numCreezies)


async def creezy_state_log_loop(event_filters, poll_interval):
    while True:
        # if roomState.check_web3_connection():
        if True:
            for curEventFilter in event_filters:
                for event in curEventFilter.get_new_entries():
                    handle_new_creezy_state(event)
        await asyncio.sleep(poll_interval)


def handle_room_addr_assign():
    print("Please enter the new Room contract address or q to cancel: ")
    addr = input("Contract Address")
    if roomState.web3.isAddress(addr):
        roomStateAddress = addr
    elif addr == 'q':
        print("cancelling...")
    else:
        print("Error in address format, please try again")
        handle_room_addr_assign()


def handle_choice(choice):
    if choice == "init":
        daliCreezy.dali_init()
    elif choice == "scan":
        daliCreezy.dali_search_address()
    elif choice == "identify":
        print("not implemented yet")
    elif choice == "roomaddr":
        handle_room_addr_assign()
    elif choice == "startthread":
        print("not implemented yet")
    elif choice == "join":
        print("not implemented yet")
    elif choice == "start":
        if pending_flag:
            monitor(True)
        else:
            monitor(False)
    elif choice == "startpending":
        monitor(True)
    elif choice == "call":
        call_DALI_states()
    elif choice == "query":
        index = input("Enter Luminaire to Query \n")
        query_DALI_luminaire(int(index))
    elif choice == "startwdali":
        print("Not Implemented yet")
    elif choice == "connectVCU":
        handle_VCU_connect()
    elif choice == "coap" or choice == "pending" or choice == "offset":
        handle_toggle(choice)
    elif choice == "setoffset":
        handle_set_offset()
    else:
        print("Invalid Choice, please try again")
    display_menu()


def handle_set_offset():
    global offset_frequency_s
    print("Current offset frequency is :  " + str(offset_frequency_s) + " seconds")
    freq = input("Please enter the offset frequency in s (3600s is 1h, 86400 is 24h")
    offset_frequency_s = freq
    print("Frequency set!")


def display_creezy_text():
    print("   _____                         _____ _")
    print("  / ____|                       |  __ (_)")
    print(" | |     _ __ ___  ___ _____   _| |__) | ")
    print(" | |    | '__/ _ \/ _ \_  / | | |  ___/ |")
    print(" | |____| | |  __/  __// /| |_| | |   | |")
    print("  \_____|_|  \___|\___/___|\__, |_|   |_|")
    print("                            __/ |        ")
    print("                           |___/         \n")
    print("By Creol - Creation to Control \n")
    print("Version 0.1 Pre-Alpha")


def display_menu():
    print("Please enter an option for this CreezyPi from the following:    \n")
    print("Initialize a new DALI network:                                init")
    print("Scan an existing DALI network for addresses:                  scan")
    print("Identify devices from short addresses:                    identify")
    print("Assign Room contract address:                             roomaddr")
    print("Initialize a Thread Network:                           startthread")
    print("Join a Thread Network:                                        join")
    print("Recall Current DALI States:                                   call")
    print("Start CreezyPi Monitoring/Control:                           start")
    print("Connect VCU Offset Contract:                            connectVCU")
    print("Toggle Offsetting                                           offset")
    print("Toggle CoaP                                                   coap")
    print("Toggle use of Pending Txns                                 pending")
    print("Set Offset frequency                                     setoffset")
    print("Set Offset Parameters                                 setVCUparams")

    choice = input("Select: \n")
    handle_choice(choice)


def handle_toggle(choice):
    global coap_flag
    global pending_flag
    global offset_flag

    if choice == "coap":
        coap_flag = not coap_flag
        print("CoAP set to: " + str(coap_flag))
    elif choice == "pending":
        pending_flag = not pending_flag
        print("Pending Flag set to: " + str(pending_flag))
    elif choice == "offset":
        offset_flag = not offset_flag
        print("Offset Flag set to: " + str(offset_flag))


def enable_web3_monitor(pendingFlag):
    """
	Build the web3 filters to send to the Infura node. These filters are used to watch for events.
	TODO: The filters unfortunately uninstall and are not permanent meaning that they do not work on Infura. 2 Options
		  either, host node, or refactor for Contract.events.
	:param pendingFlag: Whether or not to accept "pending txns"
	:return: No return
	"""
    # Build Filters
    print("Building Web3 Filters...")
    # Individual LED Filters
    pendingFilter = 'latest'
    if pendingFlag:
        pendingFilter = 'pending'

    LED_State_Filters = list()
    LED_Dim_Filters = list()
    for i in LEDStates:
        LED_State_Filters.append(i.events.stateUpdated.createFilter(fromBlock='latest', toBlock=pendingFilter))
        LED_Dim_Filters.append(i.events.dimUpdated.createFilter(fromBlock='latest', toBlock=pendingFilter))
    # Creezy Management Filters
    newCreezy_Filter = roomState.RoomState.events.newCreezy.createFilter(fromBlock='latest')
    delCreezy_Filter = roomState.RoomState.events.delCreezy.createFilter(fromBlock='latest')
    # Creezy Params Filters
    newCreezyCoapAddr_Filter = roomState.RoomState.events.newCreezyCoapAddr.createFilter(fromBlock='latest')
    # Room Group Filters
    # Filter is setup only for this contract address
    newGroup_Filter = roomState.RoomState.events.newGroup.createFilter(fromBlock='latest')
    groupRemoved_Filter = roomState.RoomState.events.groupDeleted.createFilter(fromBlock='latest')

    filters = [newCreezy_Filter, delCreezy_Filter, newCreezyCoapAddr_Filter, newGroup_Filter, groupRemoved_Filter]

    return filters, LED_State_Filters, LED_Dim_Filters


# TODO: Optimize and Run checks against Current Status of DALI luminaire
def call_DALI_states():
    """
	Recall the current DALI States based on the LED addresses.
	:return:
	"""
    # Check States on Room Contract First
    light_levels = list()
    light_states = list()
    daliShortAddr = list()
    j = 0
    for i in LEDStates:
        light_levels.append(i.functions.getDim().call())
        light_states.append(i.functions.getState().call())
        daliShortAddr.append(i.functions.getDALIShortAddress().call())

        # convert to direct command
        direct_short = (daliShortAddr[j] << 1)
        direct_short = '{0:0{1}X}'.format(direct_short, 2)
        print(direct_short)
        # Send State Command To the LED
        if light_states[j]:
            dimSet = '{:02X}'.format(light_levels[j])
            daliCreezy.dali_send_16_cmd(str(direct_short), str(dimSet), 0)
        else:
            daliCreezy.dali_send_16_cmd(str(direct_short), daliCreezy.daliOFF, 0)
        j += 1


def query_DALI_luminaire(index_light):
    """
	Query a specific DALI Short address on the setting
	:param index_light: Index from 0-63 of DALI
	:return: returns Int of the light level.
	"""
    # Query Specific Lamp on DIM setting./Status
    addr = (index_light * 2) + 1
    # Clear Buffer

    daliCreezy.daliSerial.read(8)

    # Individual
    daliCreezy.daliSerial.write(('h%02XA0\n' % addr).encode())

    # Read Response
    resp = daliCreezy.daliSerial.read(1).decode()

    if resp == 'J':
        # Read Light Level
        lvl = daliCreezy.daliSerial.read(2)
        if debug:
            print("Light Level of " + str(index_light) + " is : " + str(lvl))
        return int(lvl, 16)


# Queries and then Reports State to DLT requires valid index on DLT and DALI
# TODO: Needs simplificaton, too much repeated code
def report_DALI_state(index_light, nonce):
    dim_lvl = query_DALI_luminaire(index_light)
    dlt_dim_lvl = LEDStates[index_light].functions.getDim().call()
    dlt_state = LEDStates[index_light].functions.getState().call()
    confirm_delay = 1

    # DALI is off and DLT is Off
    if dim_lvl is not None and dim_lvl == 0 and dlt_state is False:
        if debug:
            print("Conditions Match, no Update")
        return
    # DALI is off and DLT is ON
    elif dim_lvl is not None and dim_lvl == 0 and dlt_state is True:
        if debug:
            print("DALI OFF, DLT ON")
        # Send DLT Txn Here
        chainId = int(roomState.web3.eth.chainId, 16)
        gasEstimate = 60000
        # LEDStates[index_light].functions.updateState(True).estimateGas({'gas': 10000000000, 'gasPrice': roomState.web3.toWei("4", 'gwei'), 'nonce': nonce, 'chainId': chainId, 'from': '0xcC446D7F63E09B29c427C9b5310976e6E6ABae73'})

        # TODO: Dynamic Gas Pricing
        light_txn = LEDStates[index_light].functions.updateState(False).buildTransaction(
            {'gas': gasEstimate, 'gasPrice': roomState.web3.toWei(4, 'gwei'), 'nonce': nonce, 'chainId': chainId,
             'from': creezyPiAddress})
        signed_txn = roomState.web3.eth.account.signTransaction(light_txn, creezyPrivKey)
        sent_txn = roomState.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(roomState.web3.toHex(signed_txn.hash))
        tx_receipt = None
        tx_lookup = roomState.web3.toHex(signed_txn.hash)
        # Wait til it hits the infura node pool
        time.sleep(confirm_delay)
        if debug:
            print("Waiting for Confirmation...")
        while tx_receipt is None:
            try:
                tx_receipt = roomState.web3.eth.getTransactionReceipt(str(tx_lookup))
                time.sleep(confirm_delay)
            except:
                pass
        print("Confirmed!")
        print(
            "DLT State Updated for Light: " + str(index_light) + " at address: " + str(LEDStates[index_light].address))
    # DALI is on and DLT is Off
    # TODO: Check also the dim level
    elif dim_lvl is not None and dim_lvl != 0 and dlt_state is False:
        if debug:
            print("DALI ON, DLT OFF")
        # Send DLT Txn Here
        chainId = int(roomState.web3.eth.chainId, 16)
        gasEstimate = 60000
        # LEDStates[index_light].functions.updateState(True).estimateGas({'gas': 10000000000, 'gasPrice': roomState.web3.toWei("4", 'gwei'), 'nonce': nonce, 'chainId': chainId, 'from': '0xcC446D7F63E09B29c427C9b5310976e6E6ABae73'})

        # TODO: Dynamic Gas Pricing
        light_txn = LEDStates[index_light].functions.updateState(True).buildTransaction(
            {'gas': gasEstimate, 'gasPrice': roomState.web3.toWei(4, 'gwei'), 'nonce': nonce, 'chainId': chainId,
             'from': creezyPiAddress})
        signed_txn = roomState.web3.eth.account.signTransaction(light_txn, creezyPrivKey)
        sent_txn = roomState.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(roomState.web3.toHex(signed_txn.hash))
        tx_receipt = None
        tx_lookup = roomState.web3.toHex(signed_txn.hash)
        # Wait til it hits the infura node pool
        time.sleep(confirm_delay)
        if debug:
            print("Waiting for Confirmation...")
        while tx_receipt is None:
            try:
                tx_receipt = roomState.web3.eth.getTransactionReceipt(str(tx_lookup))
                time.sleep(confirm_delay)
            except:
                pass
        print("Confirmed!")
        print(
            "DLT State Updated for Light: " + str(index_light) + " at address: " + str(LEDStates[index_light].address))
        # DALI On and DLT now ON
        # Check the dim levels as well.
        # Assume that if it died and came back on, to set it to the DIM level of the DLT
        # TODO: Combine to one function
        if dlt_dim_lvl != dim_lvl:
            if debug:
                print("DLT dim lvl doesnt match actual")
            if dim_lvl == 254 and dlt_dim_lvl != 254:
                if debug:
                    print("Assumed Failure or Power Loss restoration")
                # convert to direct command
                direct_short = (index_light << 1)
                direct_short = '{0:0{1}X}'.format(direct_short, 2)
                # Send State Command To the LED
                print("Adjusting Dim...")
                dimSet = '{:02X}'.format(dlt_dim_lvl)
                daliCreezy.dali_send_16_cmd(str(direct_short), str(dimSet), 0)
            else:
                # Send DLT Txn Here
                chainId = int(roomState.web3.eth.chainId, 16)
                gasEstimate = 60000
                # TODO: Dynamic Gas Pricing
                light_txn = LEDStates[index_light].functions.updateDim(dim_lvl).buildTransaction(
                    {'gas': gasEstimate, 'gasPrice': roomState.web3.toWei(4, 'gwei'), 'nonce': nonce + 1,
                     'chainId': chainId, 'from': creezyPiAddress})
                signed_txn = roomState.web3.eth.account.signTransaction(light_txn, creezyPrivKey)
                roomState.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
                print(roomState.web3.toHex(signed_txn.hash))
                tx_receipt = None
                tx_lookup = roomState.web3.toHex(signed_txn.hash)
                # Wait til it hits the infura node pool
                time.sleep(confirm_delay)
                if debug:
                    print("Waiting for Confirmation...")
                while tx_receipt is None:
                    try:
                        tx_receipt = roomState.web3.eth.getTransactionReceipt(str(tx_lookup))
                        time.sleep(confirm_delay)
                    except:
                        pass
                print("Confirmed!")
                print("DLT DIM Updated")

    # DALI is on and DLT is ON
    elif dim_lvl is not None and dim_lvl != 0 and dlt_state is True:
        if debug:
            print("DALI ON, DLT ON")
        if dlt_dim_lvl != dim_lvl:
            if debug:
                print("DLT dim lvl doesnt match actual")
            # Send DLT Txn Here
            chainId = int(roomState.web3.eth.chainId, 16)
            # nonce = roomState.web3.eth.getTransactionCount('0xcC446D7F63E09B29c427C9b5310976e6E6ABae73')
            gasEstimate = 60000
            # LEDStates[index_light].functions.updateDim(254).estimateGas({'gas': 10000000000, 'gasPrice': roomState.web3.toWei("4", 'gwei'), 'nonce': nonce, 'chainId': chainId, 'from': '0xcC446D7F63E09B29c427C9b5310976e6E6ABae73'})

            # TODO: Dynamic Gas Pricing
            light_txn = LEDStates[index_light].functions.updateDim(dim_lvl).buildTransaction(
                {'gas': gasEstimate, 'gasPrice': roomState.web3.toWei(4, 'gwei'), 'nonce': nonce, 'chainId': chainId,
                 'from': creezyPiAddress})
            signed_txn = roomState.web3.eth.account.signTransaction(light_txn, creezyPrivKey)
            roomState.web3.eth.sendRawTransaction(signed_txn.rawTransaction)

            print(roomState.web3.toHex(signed_txn.hash))
            tx_receipt = None
            tx_lookup = roomState.web3.toHex(signed_txn.hash)
            # Wait til it hits the infura node pool
            time.sleep(confirm_delay)
            if debug:
                print("Waiting for Confirmation...")
            while tx_receipt is None:
                try:
                    tx_receipt = roomState.web3.eth.getTransactionReceipt(str(tx_lookup))
                    time.sleep(confirm_delay)
                except:
                    pass
            print("Confirmed!")
            print("DLT DIM Updated")
        else:
            return
    # Potentially lost power or is dead, for now treat as OFF,
    # TODO: Enable LEDState to have failure flag
    elif dim_lvl is None and dlt_state is True:
        # First Confirm the failure.
        for i in range(3):
            dim_lvl = query_DALI_luminaire(index_light)
            print(dim_lvl)
            if dim_lvl is not None:
                break
        # Confirmed Power Failure
        if dim_lvl is None:
            if debug:
                print("No Dim Lvl Read, Potential Power Loss or Failure Detected")
            chainId = int(roomState.web3.eth.chainId, 16)
            gasEstimate = 60000
            # TODO: Dynamic Gas Pricing
            light_txn = LEDStates[index_light].functions.updateState(False).buildTransaction(
                {'gas': gasEstimate, 'gasPrice': roomState.web3.toWei(4, 'gwei'), 'nonce': nonce, 'chainId': chainId,
                 'from': creezyPiAddress})
            signed_txn = roomState.web3.eth.account.signTransaction(light_txn, creezyPrivKey)
            sent_txn = roomState.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
            print(roomState.web3.toHex(signed_txn.hash))
            tx_receipt = None
            tx_lookup = roomState.web3.toHex(signed_txn.hash)
            # Wait til it hits the infura node pool
            time.sleep(confirm_delay)
            if debug:
                print("Waiting for Confirmation...")
            while tx_receipt is None:
                try:
                    tx_receipt = roomState.web3.eth.getTransactionReceipt(str(tx_lookup))
                    time.sleep(confirm_delay)
                except:
                    pass
            print("Confirmed!")
            print(
                "Potential Power Failure Reported at Light : " + str(index_light) + " at address: " + str(
                    LEDStates[index_light].address))
    # Assume Dead already for now
    elif dim_lvl is None and dlt_state is False:
        if debug:
            print("Luminaire:  " + str(index_light) + " must be dead or off")


def handle_VCU_connect():
    attempts = 0
    while (attempts < 3):
        address = input("Please provide the Eth address of the VCU Offset contract")
        if roomState.web3.isAddress(address):
            roomState.connect_VCU_Offsetter(address)
            attempts = 3
            print("Successfully Connected")
        else:
            print("Invalid Address format , please try again")
            attempts = attempts + 1


def load_web3_wallet():
    """
	Creates a web3 wallet for use. Currently feature is not used. But is for future commissioning structure.
	:return:
	"""
    global creezyWallet
    creezyWallet = wallet.create_wallet(network="ETH", seed=creezyPhrase, children=0)


# TODO: Pull dali addresses from DLT
async def dali_state_log_loop(poll_interval):
    """
	Checks the DALI state and compares against the Smart Contract
	:param poll_interval: set in ms for number of times to poll within the interval
	:return: no return
	"""
    while True:
        j = 0
        if True:
            # if roomState.check_web3_connection():
            for i in LEDStates:
                # Pull nonce count
                # TODO: Make this nonce count come from the CreezyWallet address
                idx_nonce = roomState.web3.eth.getTransactionCount('0xcC446D7F63E09B29c427C9b5310976e6E6ABae73')
                report_DALI_state(j, idx_nonce)
                j += 1
        await asyncio.sleep(poll_interval)


async def offset_state_loop(poll_interval):
    """
	Begins the offset process periodically
	:param poll_interval: Poling
	:type poll_interval: int seconds
	:return:
	:rtype:
	"""
    idx_nonce = roomState.web3.eth.getTransactionCount('0xcC446D7F63E09B29c427C9b5310976e6E6ABae73')
    chainId = int(roomState.web3.eth.chainId, 16)
    gasEstimate = 60000
    while True:
        offset_txn_1 = roomState.VCUOffset.functions.sendOffset(LED_Group_ID, VCUIndexes,
                                                                country_code).buildTransaction({
            'gas': gasEstimate, 'gasPrice': roomState.web3.toWei(4, 'gwei'), 'nonce': idx_nonce, 'chainId': chainId,
            'from':
                creezyPiAddress
        })
        tx_receipt_1 = sign_send_confirm_txn(offset_txn_1)

        print("Confirmed ! Now waiting for Provable Response")

        print("Waiting for TokensReady Event...")

        """
		BUNCH OF LOGIC FOR WAITING HERE
		
		"""

        tokensReady_filter = roomState.VCUOffset.events.TokensReady(fromBlock=tx_receipt_1.blockNumber)
        tokensReady = None

        while tokensReady is None:
            try:
                returnedArray = tokensReady_filter.get_new_entries()
                if returnedArray != []:
                    tokensReady = returnedArray

            except:
                pass
            await asyncio.sleep(1)

        offset_txn_2 = roomState.VCUOffset.functions.finishOffset(VCUIndexes, VCUOwner).buildTransaction({
            'gas': gasEstimate, 'gasPrice': roomState.web3.toWei(4, 'gwei'), 'nonce': idx_nonce, 'chainId': chainId,
            'from':
                creezyPiAddress
        })
        tx_receipt_2 = sign_send_confirm_txn(offset_txn_2)
        await asyncio.sleep(poll_interval)


def sign_send_confirm_txn(built_txn):
    signed_txn = roomState.web3.eth.account.signTransaction(built_txn, creezyPrivKey)

    roomState.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    tx_receipt = None

    if debug:
        print("Waiting for Confirmation...")
    while tx_receipt is None:
        try:
            roomState.web3.eth.waitForTransactionReceipt(signed_txn.hash)
        except:
            pass
    if tx_receipt is not None:
        return tx_receipt
    else:
        return 0


def monitor_DALI():
    """
	Artifact of a previous function, is used in KIBRA configuration
	TODO: Merge with creol-KIBRA
	:return: None
	"""
    print("Waiting for DALI state changes")


def threaded_main():
    """
	Threaded version of the monitor function to address timeout errors.
	:return:
	"""


# TODO: Check sequence to ensure we are good to engage
def monitor(pendingFlag):
    # Start Web3 Monitoring
    print("Monitoring Web3...")
    timeToError = 0

    global LEDLoopTimer

    # creezy_filters, LED_State_Filters, LED_Dim_Filters = enable_web3_monitor()

    tries = 10
    for i in range(tries):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        timeToError = time.time()
        print("Fetching Events...")
        timeToError = time.time()
        creezy_filters, LED_State_Filters, LED_Dim_Filters = enable_web3_monitor(pendingFlag)
        try:
            # Poll Asynchronously every 1 seconds tar
            if offset_flag:
                loop.run_until_complete(asyncio.gather(
                    (led_state_log_loop(LED_State_Filters, LEDLoopTimer)),
                    (led_dim_log_loop(LED_Dim_Filters, LEDLoopTimer)),
                    (creezy_state_log_loop(creezy_filters, LEDLoopTimer)),
                    (dali_state_log_loop(1800)),
                    (offset_state_loop(offset_frequency_s))
                ))
            else:
                loop.run_until_complete(asyncio.gather(
                    (led_state_log_loop(LED_State_Filters, LEDLoopTimer)),
                    (led_dim_log_loop(LED_Dim_Filters, LEDLoopTimer)),
                    (creezy_state_log_loop(creezy_filters, LEDLoopTimer)),
                    (dali_state_log_loop(1800))
                ))

            # state_log_loop(Room_Filter, 2)))
        except ValueError as e:
            print(str(e))
            print("Exception: Filters Uninstalled")
            elapsed = time.time() - timeToError
            print("Elapsed Time: " + str(elapsed))

            pass
        # finally:
        # print("Finally Reached....")
        # loop.close()
        loop.close()


def kibra_main():
    """
	Main function for use with Kirale Dongle, currently a WIP
	:return: None
	"""
    load_modules()
    display_creezy_text()
    load_contract_abis()
    if dali_enable:
        handle_dali_enable()
        call_DALI_states()
    monitor(False)


def main():
    """
	Main function. Deploys all modules to run the basic Creezy functions.
	:return: None
	"""
    global pending_flag
    global coap_flag
    global offset_flag

    load_modules()
    display_creezy_text()
    load_contract_abis()
    if dali_enable:
        handle_dali_enable()
        call_DALI_states()
    display_menu()


if __name__ == '__main__':
    main()
