#! /usr/bin/env python3

from time import sleep
from telnetlib import Telnet

IPADDRESS = '192.168.178.31'
PORT = 23
TIMEOUT = 30

class DenonAvr:
    def __init__(self, ipAddress, port, timeout):
        self.session = Telnet(ipAddress, port, timeout)
        self.debug = False

    def __del__(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def setDebug(self, debugOn = True):
        self.debug = debugOn

    def send(self, command, timeToWaitForResponse = 0):
        self.session.write(f'{command}\r'.encode())

        if (self.debug):
            print(f'Sending: {command}\nWait for response: {timeToWaitForResponse}')

        if (timeToWaitForResponse > 0):
            sleep(timeToWaitForResponse)
            result = self.session.read_eager().decode('ascii')

            if(self.debug):
                print(f'Result: {result}')
                return result

    def changeInput(self, channelName):
        lookupTable = {
            'computer': 'SICD',
            'mediapc': 'SIMPLAY',
            'tv': 'SISAT/CBL',
        }

        if channelName not in lookupTable:
            raise ValueError(f'Do not know what to do with {channelName}')
        else:
            self.send(lookupTable[channelName])

    def power(self, state):
        allowedStates = ['ON', 'STANDBY', '?']

        if state.upper() not in allowedStates:
            raise ValueError(f'Do not know what to do with {state}')
        else:
            self.send(f'PW{state.upper()}', 1)

    def volume(self, volume):
        if 0 <= volume <= 80:
            self.send(f'MV{volume}')
        else:
            raise ValueError(f'Volume out of bound (0-80): {volume}')

with DenonAvr(IPADDRESS, PORT, TIMEOUT) as avr:
    # avr.setDebug()

    avr.power('on')
    avr.changeInput('computer')
    avr.volume(50)
