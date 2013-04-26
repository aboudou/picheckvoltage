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
        conn.sendall(str(ADCLOW)+'|'
        +str(ret)+'|'
        +str(ADCHIGH)+'||'
        +str(BATNUMBER*LOWBATVOLT)+'|'
        +str((ret*(BATNUMBER*FULLBATVOLT)/1024)*VCOMP)+'|'
        +str(BATNUMBER*FULLBATVOLT))
        conn.close()

# Called on process interruption. Set all pins to "Input" default mode.
def endProcess(signalnum = None, handler = None):
    GPIO.cleanup()
    socketThread._Thread__stop()
    if STATUSGOODBAT == 1:
        try:
            p = subprocess.Popen(NOBAT_SCRIPT_PATH, stdout=subprocess.PIPE)
        except OSError:
            print ("Could not execute " + NOBAT_SCRIPT_PATH)
    exit(0)

if DEBUGMSG == 1:
  print("Batteries high voltage:       " + str(VHIGHBAT))
  print("Batteries low voltage:        " + str(VLOWBAT))
  print("Batteries dangerous voltage:  " + str(VDNGBAT))
  print("ADC high voltage value:       " + str(ADCHIGH))
  print("ADC low voltage value:        " + str(ADCLOW))
  print("ADC dangerous voltage value:  " + str(ADCDNG))

# Put pins to out mode and low state.
def initPins():
    GPIO.setup(GOODVOLTPIN, GPIO.OUT)
    GPIO.setup(LOWVOLTPIN, GPIO.OUT)
    GPIO.setup(KILLPIN, GPIO.OUT)
    GPIO.output(GOODVOLTPIN, GPIO.LOW)
    GPIO.output(LOWVOLTPIN, GPIO.LOW)
    GPIO.output(KILLPIN, GPIO.LOW)


### Main part

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
            try:
                p = subprocess.Popen(NOBAT_SCRIPT_PATH, stdout=subprocess.PIPE)
                STATUSNOBAT = 1
                STATUSDNGBAT = 0
                STATUSLOWBAT = 0
                STATUSGOODBAT = 0
            except OSError:
                print ("Could not execute " + NOBAT_SCRIPT_PATH)

    elif ret < ADCDNG:
        # Dangerous battery voltage : we switch OK LED off, KO LED on,
        #   and run DNGBAT_SCRIPT_PATH
        GPIO.output(GOODVOLTPIN, GPIO.LOW)
        GPIO.output(LOWVOLTPIN, GPIO.HIGH)
        GPIO.output(KILLPIN, GPIO.LOW)
        if STATUSDNGBAT == 0:
            try:
                p = subprocess.Popen(DNGBAT_SCRIPT_PATH, stdout=subprocess.PIPE)
                STATUSNOBAT =0 
                STATUSDNGBAT = 1
                STATUSLOWBAT = 0
                STATUSGOODBAT = 0
            except OSError:
                print ("Could not execute " + DNGBAT_SCRIPT_PATH)
    
    elif ret < ADCLOW:
        # Low battery voltage : we switch OK LED off, KO LED on, 
        #   and run KOBAT_SCRIPT_PATH
        GPIO.output(GOODVOLTPIN, GPIO.LOW)
        GPIO.output(LOWVOLTPIN, GPIO.HIGH)
        GPIO.output(KILLPIN, GPIO.HIGH)
        if STATUSLOWBAT == 0:
            try:
                p = subprocess.Popen(KOBAT_SCRIPT_PATH, stdout=subprocess.PIPE)
                STATUSNOBAT = 0
                STATUSDNGBAT = 0 
                STATUSLOWBAT = 1 
                STATUSGOODBAT = 0
            except OSError:
                print ("Could not execute " + KOBAT_SCRIPT_PATH)

    else:
        # Normal battery voltage : we switch OK LED on, KO LED off, 
        #   and OKBAT_SCRIPT_PATH
        GPIO.output(GOODVOLTPIN, GPIO.HIGH)
        GPIO.output(LOWVOLTPIN, GPIO.LOW)
        GPIO.output(KILLPIN, GPIO.HIGH)
        if STATUSGOODBAT == 0:
            try:
                p = subprocess.Popen(OKBAT_SCRIPT_PATH, stdout=subprocess.PIPE)
                STATUSNOBAT = 0
                STATUSDNGBAT = 0
                STATUSLOWBAT = 0
                STATUSGOODBAT = 1
            except OSError:
                print ("Could not execute " + OKBAT_SCRIPT_PATH)

    # Pause before starting loop once again
    time.sleep(REFRESH_RATE / 1000)
