"""
" Edit below this line to fit your needs
"""

## Path of the scripts which will run by checkvoltage
# Script to run when no battery is plugged (array with script then parameters)
NOBAT_SCRIPT_PATH = ["/root/raspberrypi/movingraspi/MovingRaspiPlus/Server/movingraspi.sh", "stop"]
# Script to run when battery voltage is dangerously low (array with script then
#   parameters)
DNGBAT_SCRIPT_PATH = ["/root/pcvscripts/batterymail.sh", "&"]
# Script to run when battery voltage is low (array with script then parameters)
KOBAT_SCRIPT_PATH = ["/root/raspberrypi/movingraspi/MovingRaspiPlus/Server/movingraspi.sh", "stop"]
# Script to run when battery voltage is good (array with script then parameters)
OKBAT_SCRIPT_PATH = ["/root/raspberrypi/movingraspi/MovingRaspiPlus/Server/movingraspi.sh", "start"]

# GPIO (BOARD numbering scheme) pin for good voltage LED
GOODVOLTPIN = 11
# GPIO (BOARD numbering scheme) pin for low voltage LED
LOWVOLTPIN = 12
# GPIO (BOARD numbering scheme) pin for kill switch (LOW value to stop powering
#   assembly) 
KILLPIN = 13

## Define voltages
# Number of batteries in series
BATNUMBER = 8.0
#BATNUMBER = 3.0
# Fully charged voltage (for a single battery); 
#   i.e. 1.4V for a NiMH battery, or 4.2V for a LiPo battery
FULLBATVOLT = 1.4
#FULLBATVOLT = 4.2
# Discharged voltage (for a single battery); 
#   i.e. 1.05V for a NiMH battery, or 3.1V for a LiPo battery
#   You should use a conservative value in order to avoid destructive
#   discharging
LOWBATVOLT = 1.05
#LOWBATVOLT = 3.1
# Dangerous voltage (for a single battery);
#   i.e. 1.0V for a NiMH battery, or 3.05V for a LiPo battery
#   You should really not go below this voltage.
DNGBATVOLT = 1.0
#DNGBATVOLT = 3.05

# Value (in ohms) of the lower resistor from the voltage divider, connected to
#   the ground line (1 if no voltage divider). Default value (3900) is for a 
#   battery pack of 8 NiMH batteries, providing 11.2V max, stepped down to about
#   3.2V max.
LOWRESVAL = 3900
# Value (in ohms) of the higher resistor from the voltage divider, connected to 
#   the positive line (0 if no voltage divider). Default value (10000) is for a
#   battery pack of 8 NiMH batteries, providing 11.2V max, stepped down to about
#   3.2V max.
HIGHRESVAL = 10000
# Voltage value measured by the MCP3008 when batteries are fully charged
# It should be near 3.3V due to Raspberry Pi GPIO compatibility)
VHIGHBAT = (BATNUMBER*FULLBATVOLT)*(LOWRESVAL)/(LOWRESVAL+HIGHRESVAL)
# Voltage value measured by the MCP3008 when batteries are discharged
VLOWBAT = (BATNUMBER*LOWBATVOLT)*(LOWRESVAL)/(LOWRESVAL+HIGHRESVAL)
# Voltage value measured by the MCP3008 when batteries voltage is dangerously
#   low
VDNGBAT = (BATNUMBER*DNGBATVOLT)*(LOWRESVAL)/(LOWRESVAL+HIGHRESVAL)

# ADC voltage reference (3.3V for Raspberry Pi)
ADCVREF = 3.3

# Compensation due to the difference between ADC voltage reference and 
#   max value for voltage through resistor divider
#   i.e. : with the given resistances values, VREF is 3.3 V, and max voltage
#   through resistor divider is about 3.14V, leading to about 4.8% deviation.
# This compensation is used to correct computed battery voltage return by
#   network queries
VCOMP = 1+(ADCVREF-VHIGHBAT)/ADCVREF

## Define expected ADC values
# MCP23008 channel to use (from 0 to 7)
ADCCHANNEL = 0
# MCP23008 should return this value when batteries are fully charged
#  * 3.3 is the reference voltage (got from Raspberry Pi's +3.3V power line)
#  * 1024.0 is the number of possible values (MCP23008 is a 10 bit ADC)
ADCHIGH = VHIGHBAT / (ADCVREF / 1024.0)
# MCP23008 should return this value when batteries are discharged
#  * 3.3 is the reference voltage (got from Raspberry Pi's +3.3V power line)
#  * 1024.0 is the number of possible values (MCP23008 is a 10 bit ADC)
ADCLOW = VLOWBAT / (ADCVREF / 1024.0)
# MCP23008 should return this value when batteries atteigns dangerous voltage
#  * 3.3 is the reference voltage (got from Raspberry Pi's +3.3V power line)
#  * 1024.0 is the number of possible values (MCP23008 is a 10 bit ADC)
ADCDNG = VDNGBAT / (ADCVREF / 1024.0)
# MCP should return a value lower than this one when no battery is plugged.
# You should not use 0 because value is floatting around 0 / 150 when nothing
#  is plugged to a analog channel. 
ADCUNP = 300 # No battery plugged

# Refresh rate (ms)
REFRESH_RATE = 1000

# Hostname or IP address to listen for network queries. '' for all interfaces
TCPHOST = ''
# TCP port
TCPPORT = 50007

# Enable to possibility to push battery values to SIGFOX network
#   http://www.sigfox.com/ for more information.
SIGFOX_ENABLE = 0
# SIGFOX device serial device
SIGFOX_DEVICE = "/dev/ttyUSB0"
# SIGFOX device baud rate
SIGFOX_DEV_BR = 9600
# SIGFOX device byte size (5 to 8)
SIGFOX_DEV_BS = 8
# SIGFOX device parity ("[N]one", "[E]ven", "[O]dd", "[M]ark", "[S]pace")
SIGFOX_DEV_PAR = "N"
# SIGFOX device stop bits (1, 1.5, 2)
SIGFOX_DEV_SB = 1
# SIGFOX push rate (ms, MUST be a multiple of REFRESH_RATE)
SIGFOX_PUSH_RATE = 300000

# Display some debug values when set to 1, and nothing when set to 0
DEBUGMSG = 0
