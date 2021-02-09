# Title: Event Listener
#   ______               _     _      _     _
#  |  ____|             | |   | |    (_)   | |
#  | |____   _____ _ __ | |_  | |     _ ___| |_ ___ _ __   ___ _ __
#  |  __\ \ / / _ \ '_ \| __| | |    | / __| __/ _ \ '_ \ / _ \ '__|
#  | |___\ V /  __/ | | | |_  | |____| \__ \ ||  __/ | | |  __/ |
#  |______\_/ \___|_| |_|\__| |______|_|___/\__\___|_| |_|\___|_|
#
#
# Author: Joshua Bijak
# Date:  07/05/2019
# Desc:  Boot up script for CreezyPi nodes to connect to Ethereum and begin listening on specified
#        Contract addresses for events pertaining to their own micro networks. Manages CoAP routing is message is found
#        in another micro network.
# Changelog: 07/05/2019 -  Initial Log.
#            Currently script is manual, requries infura node or personal node to be provided
#            Aim is to abstract node providing elsewhere
import json
import time
import logging
import getopt
import sys
import socket

#Import Ethereum functionality
from web3 import Web3, HTTPProvider,WebsocketProvider
#Import CoAP messaging for use with Thread
from coapthon.client.helperclient import HelperClient
from coapthon.utils import parse_uri

#Specify Infura Node
infura_wss_test = WebsocketProvider("wss://rinkeby.infura.io/ws/v3/6f1f8915d9154cefb93faef07e694e41")
web3 =  Web3([infura_wss_test])

#Temporarily HardCoded Address for Testing
coap_uri = "coap://[fdde:ad00:beef:0:7e94:f3df:951f:c781]/light"
coap_pay = b"2"

#Check Infura Connection
if web3.isConnected():
	print("wss connection successful")
else:
	print("Connection Error: Please check settings")


# Load Contract ABI
#   TODO: Load contract ABI from Compiled Contract in git submodule.

LEDContractABI =  json.loads('[{"constant":false,"inputs":[],"name":"renounceOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"newState","type":"bool"}],"name":"updateState","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"defaultState","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"name":"updatedState","type":"bool"}],"name":"stateUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"previousOwner","type":"address"},{"indexed":true,"name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"constant":true,"inputs":[],"name":"currentState","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"isOwner","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"}]')
LEDAddress = '0xA3f8A74d4c4cD907dA0dECDff40deF9b96496D1c'
LEDState = web3.eth.contract(address=LEDAddress, abi=LEDContractABI)

#Temporary Hardcoded Address for Route finding
# TODO:
host = "fdde:ad00:beef:0:7e94:f3df:951f:c781"
path = "coap://[fdde:ad00:beef:0:7e94:f3df:951f:c781]:5683/light"
port = 5683
#DALI - Arduino Hat Payload
op = "PUT"
payload = b"2"

#Attempt a sanity check by connecting to the remote address
try:
    tmp = socket.gethostbyname(host)
    host = tmps
except socket.gaierror:
    pass

#Send a PUT command to the connected address
host, port, path = parse_uri(path)
client = HelperClient(server=(host, port))
print("Sending Put")
response = client.put(path, payload)
print((response.pretty_print()))
client.stop()

#Show loaded contract address
print("LEDContract Loaded at", LEDAddress)
listener_enable = True
currentLEDState = LEDState.functions.currentState().call()

#Begin listening to network
while listener_enable:
    print("Listening")
    print("Checking State")
    #Call to infura/private node to view contract State
    # TODO: Allow for internal node hosting (Full P9
    checkState = LEDState.functions.currentState().call()
    if currentLEDState != checkState:
        print("New State On Chain, Updating profile")
        #Send CoAP Packet Here
        print("Sending Packet")

        #Prepare Arduino C UART TX/RX Packet Here
        host = "fdde:ad00:beef:0:7e94:f3df:951f:c781"
        path = "coap://[fdde:ad00:beef:0:7e94:f3df:951f:c781]:5683/light"
        port = 5683
        op = "PUT"
        payload = b"2"
        try:
            tmp = socket.gethostbyname(host)
            host = tmps
        except socket.gaierror:
            pass

        host, port, path = parse_uri(path)
        client = HelperClient(server=(host, port))
        print("Sending Put")
        #Await Response Confirmation
        response = client.put(path, payload)
        print((response.pretty_print()))
        client.stop()
        currentLEDState = checkState  
    else:
        #delay to next block
        time.sleep(10)
