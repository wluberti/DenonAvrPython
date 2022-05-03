#! /usr/bin/env python3

"""
 * @Author: Wouter Luberti
 * @Copyright: MIT
 *
 * Full Denon protocol list can be found on:
 *    http://assets.eu.denon.com/DocumentMaster/DE/AVR2113CI_1913_PROTOCOL_V02.pdf
"""
from telnetlib import Telnet
from time import sleep

DEFAULT_WAIT = 0.3  # in seconds, RFC requires minimum of 0.2 (200 miliseconds)
IPADDRESS = '192.168.178.31'
PORT = 23
TIMEOUT = 30


class DenonAvr:
    def __init__(self, ipAddress, port, timeout):
        self.session = Telnet(ipAddress, port, timeout)

    def __del__(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def setDebug(self, debugState = 9):
        self.session.set_debuglevel(debugState)

    def send(self, command, value = '?', timeToWaitForResponse = DEFAULT_WAIT):
        """ Send a command to the Telnet interface

        command               - PW (Power), MV (Master Volume), SI (Source Input)
        value                 - Either int or str. Consult RFC for details
        timeToWaitForResponse - delay in seconds befor reading response
        """

        self.session.write(f'{command.upper()}{value}\r'.encode())

        sleep(timeToWaitForResponse)
        response = self.session.read_eager().decode('ascii').split('\r')

        return response[0][2:]

    def changeInput(self, inputName):
        lookupTable = {
            'chromecast': 'BD',
            'computer': 'CD',
            'mediapc': 'MPLAY',
            'tv': 'SAT/CBL',
            'macbook': 'DVD',
        }

        if inputName not in lookupTable:
            raise ValueError(f'Undefined inputName: {inputName}')
        else:
            forceChannel = True
            while forceChannel:
                self.send('SI', lookupTable[inputName], 1)
                checkedChannel = self.checkState('channel')

                if checkedChannel == lookupTable[inputName]:
                    forceChannel = False

    def power(self, state):
        allowedStates = ['ON', 'STANDBY', '?']

        if state.upper() not in allowedStates:
            raise ValueError(f'Undefined state: {state}')
        else:
            # RFC requires minimum of 1 second after power-on
            self.send('ZM', state.upper(), 1.3)

    def volume(self, volume):
        if not 0 <= volume <= 80:
            raise ValueError(f'Volume out of bound (0-80): {volume}')
        else:
            currentVolume = self.send('MV', volume)

            if currentVolume and int(currentVolume) != volume:
                forceVolume = True

                while forceVolume == True:
                    response = self.send('MV', volume)
                    if response == volume:
                        forceVolume = False

    def checkState(self, value):
        lookupTable = {
            'power': 'PW',
            'volume': 'ZM',
            'channel': 'SI',
        }

        if value not in lookupTable:
            raise ValueError(f'Function checkState does not support "{value}"')
        else:
            return self.send(lookupTable[value], '?', DEFAULT_WAIT * 2)


with DenonAvr(IPADDRESS, PORT, TIMEOUT) as avr:
    # avr.setDebug()
    # avr.power('standby')
    avr.power('on')
    avr.changeInput('macbook')
    avr.volume(60)
    exit(0)
