#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import array
import os
import signal
import subprocess

import threading
import socket

from config import *
from mcp3008 import *

if SIGFOX_ENABLE == 1:
  try:
    import serial
  except ImportError:
    print ("Unable to import PySerial")
    exit (-1)


STATUSNOBAT = 0
STATUSDNGBAT = 0
STATUSLOWBAT = 0
STATUSGOODBAT = 0
ret = 0

### Functions definition

def runSocketServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((TCPHOST, TCPPORT))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        conn.sendall(networkData())
        conn.close()

# Called on process interruption. Set all pins to "Input" default mode.
def endProcess(signalnum = None, handler = None):
    GPIO.cleanup()
    socketThread._Thread__stop()
    if STATUSGOODBAT == 1:
        try:
            p = subprocess.Popen(NOBAT_SCRIPT_PATH, stdout=subprocess.PIPE)
        except OSError as detail:
            print ("Could not execute " + NOBAT_SCRIPT_PATH[0] + " ", detail)

    if SIGFOX_ENABLE == 1:
        sigfox.close()

    exit(0)

# Put pins to out mode and low state.
def initPins():
    GPIO.setup(GOODVOLTPIN, GPIO.OUT)
    GPIO.setup(LOWVOLTPIN, GPIO.OUT)
    GPIO.setup(KILLPIN, GPIO.OUT)
    GPIO.output(GOODVOLTPIN, GPIO.LOW)
    GPIO.output(LOWVOLTPIN, GPIO.LOW)
    GPIO.output(KILLPIN, GPIO.LOW)

# Build data send remotely (TCP or SIGFOX network)
def networkData():
    return (str(ADCLOW)+'|'
       +str(ret)+'|'
       +str(ADCHIGH)+'||'
       +str(BATNUMBER*LOWBATVOLT)+'|'
       +str((ret*(BATNUMBER*FULLBATVOLT)/1024)*VCOMP)+'|'
       +str(BATNUMBER*FULLBATVOLT))


def sigfoxData():
    return str((ret*(BATNUMBER*FULLBATVOLT)/1024)*VCOMP)[:10]

### Main part

if DEBUGMSG == 1:
    print("Batteries high voltage:       " + str(VHIGHBAT))
    print("Batteries low voltage:        " + str(VLOWBAT))
    print("Batteries dangerous voltage:  " + str(VDNGBAT))
    print("ADC high voltage value:       " + str(ADCHIGH))
    print("ADC low voltage value:        " + str(ADCLOW))
    print("ADC dangerous voltage value:  " + str(ADCDNG))


# Get current pid
pid = os.getpid()

# Save current pid for later use
try:
    fhandle = open('/var/run/picheckvoltage.pid', 'w')
except IOError:
    print ("Unable to write /var/run/picheckvoltage.pid")
    exit(1)
fhandle.write(str(pid))
fhandle.close()

# Prepare handlers for process exit
signal.signal(signal.SIGTERM, endProcess)
signal.signal(signal.SIGINT, endProcess)

# Use Raspberry Pi board pin numbers
GPIO.setmode(GPIO.BOARD)

# Init output pins
initPins()

socketThread = threading.Thread(None, runSocketServer, None, (), {})
socketThread.daemon = True
socketThread.start()

sigfox = None;
sigfoxPush = 0;
if SIGFOX_ENABLE == 1:
    sigfox = serial.Serial(port=SIGFOX_DEVICE, 
                           baudrate=SIGFOX_DEV_BR, 
                           parity=SIGFOX_DEV_PAR,
                           stopbits=SIGFOX_DEV_SB,
                           bytesize=SIGFOX_DEV_BS)



while True:
    # Read ADC measure on channel ADCCHANNEL
    ret = readadc(ADCCHANNEL, SPICLK, SPIMOSI, SPIMISO, SPICS)
    if DEBUGMSG == 1:
      print("ADC value: " + str(ret) + " (" + str((3.3 / 1024.0) * ret) + " V)")

    if ret < ADCUNP:
        # No battery plugged : we switch all LED off, and run NOBAT_SCRIPT_PATH
        GPIO.output(GOODVOLTPIN, GPIO.LOW)
        GPIO.output(LOWVOLTPIN, GPIO.LOW)
        GPIO.output(KILLPIN, GPIO.LOW)
        if STATUSNOBAT == 0:
            STATUSNOBAT = 1
            STATUSDNGBAT = 0
            STATUSLOWBAT = 0
            STATUSGOODBAT = 0
            try:
                p = subprocess.Popen(NOBAT_SCRIPT_PATH, stdout=subprocess.PIPE)
            except OSError as detail:
                print ("Could not execute " + NOBAT_SCRIPT_PATH[0] + " ", detail)

    elif ret < ADCDNG:
        # Dangerous battery voltage : we switch OK LED off, KO LED on,
        #   and run DNGBAT_SCRIPT_PATH
        GPIO.output(GOODVOLTPIN, GPIO.LOW)
        GPIO.output(LOWVOLTPIN, GPIO.HIGH)
        GPIO.output(KILLPIN, GPIO.LOW)
        if STATUSDNGBAT == 0:
            STATUSNOBAT = 0
            STATUSDNGBAT = 1
            STATUSLOWBAT = 0
            STATUSGOODBAT = 0
            try:
                p = subprocess.Popen(DNGBAT_SCRIPT_PATH, stdout=subprocess.PIPE)
            except OSError as detail:
                print ("Could not execute " + DNGBAT_SCRIPT_PATH[0] + " ", detail)
    
    elif ret < ADCLOW:
        # Test if we were previously in dangerous status and are actually
        #   encountering a voltage bounce situation after kill switch
        #   activation. 
        if STATUSDNGBAT == 1 and ret > ADCDNGBOUNCE:
            # Low battery voltage : we switch OK LED off, KO LED on, 
            #   and run KOBAT_SCRIPT_PATH
            GPIO.output(GOODVOLTPIN, GPIO.LOW)
            GPIO.output(LOWVOLTPIN, GPIO.HIGH)
            GPIO.output(KILLPIN, GPIO.HIGH)
            if STATUSLOWBAT == 0:
                STATUSNOBAT = 0
                STATUSDNGBAT = 0 
                STATUSLOWBAT = 1 
                STATUSGOODBAT = 0
                try:
                    p = subprocess.Popen(KOBAT_SCRIPT_PATH, stdout=subprocess.PIPE)
                except OSError as detail:
                    print ("Could not execute " + KOBAT_SCRIPT_PATH[0] + " ", detail)

    else:
        # Normal battery voltage : we switch OK LED on, KO LED off, 
        #   and OKBAT_SCRIPT_PATH
        GPIO.output(GOODVOLTPIN, GPIO.HIGH)
        GPIO.output(LOWVOLTPIN, GPIO.LOW)
        GPIO.output(KILLPIN, GPIO.HIGH)
        if STATUSGOODBAT == 0:
            STATUSNOBAT = 0
            STATUSDNGBAT = 0
            STATUSLOWBAT = 0
            STATUSGOODBAT = 1
            try:
                p = subprocess.Popen(OKBAT_SCRIPT_PATH, stdout=subprocess.PIPE)
            except OSError as detail:
                print ("Could not execute " + OKBAT_SCRIPT_PATH[0] + " ", detail)

    # Push data to SIGFOX network
    if SIGFOX_ENABLE == 1:
        if sigfoxPush % (SIGFOX_PUSH_RATE / REFRESH_RATE) == 0:
            import datetime
            today = datetime.datetime.today()
            sigfox.write("at$ss=" + sigfoxData().encode("hex") + "\r")
            if DEBUGMSG == 1:
                print today.strftime("%Y-%m-%d %H:%M:%S - Sent to SIGFOX: " 
                                   + sigfoxData().encode("hex")
                                   + " a.k.a " + sigfoxData() 
                                   + "(V) in hexadecimal")
        sigfoxPush = sigfoxPush + 1
        # You don't want the counter to become too big :)
        if sigfoxPush > (SIGFOX_PUSH_RATE / REFRESH_RATE):
            sigfoxPush = 1

    # Pause before starting loop once again
    time.sleep(REFRESH_RATE / 1000)
