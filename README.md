PiCheckVoltage
==============

PiCheckVoltage is a project for the [Raspberry Pi](http://raspberrypi.org) intended to provide a mean to check voltage of a battery pack which is used to power electronic assemblies connected to the Raspberry Pi.

PiCheckVoltage is made of three hardware parts and one software part:

* A voltage regulation unit, which take voltage from the battery pack and provides a +5V regulated power line (to power some IC like port expanders, motor drivers, even Raspberry Pi itself)
* A voltage measurement unit, which check battery pack voltage after it is stepped down to a 0V to 3.3V range by a resistor divider.
* Two status LEDs, which can display if battery pack voltage is good or too low.
* A “kill switch”, which unplug battery when voltage is dangerously low.
* A program to run on the Raspberry Pi, which read mesured voltage, drive status LEDs, and can start three user provided scripts when the battery pack voltage reaches three different levels:
	* 0V level: a.k.a. unplugged battery pack
        * dangerous battery level: when voltage reaches a value which is dangerously low for the batteries
	* low battery level: when voltage reaches a value which is near to be dangerously low for the batteries
	* good battery level: when voltage is over low battery level


You can see the live electronic assembly for PiCheckVoltage on [this photo](http://www.flickr.com/photos/aboudou/8666239532/) which is used to manage [MovingRaspi](https://goddess-gate.com/dc2/index.php/pages/movingraspi.en) 

Credits
-------

“mcp3008.py” file provided with PiCheckVoltage comes from [Adafruit-Raspberry-Pi-Python-Code](https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code) GitHub repository, and is slightly modified to fit PiCheckVoltage needs.


Requirements
------------

* First of all: a Raspberry Pi
* Electronic parts to build the assembly:
	* For the status LEDs:
		* One green LED (good battery voltage status LED)
		* One yellow LED (low battery voltage status LED)
		* Two 330Ω resistors
	* For the voltage measurement unit:
		* One BCU81 transistor (act as a kill switch when batteries voltage is dangerously low) 
                * One 330Ω resistor to limit the current sent to transistor's base pin
		* One MCP3008 (ADC chip used to read battery voltage)
		* One 10kΩ (R1, connected to positive rail) and one 3.9 kΩ (R2, connected to ground rail) resistor for the voltage divider. These values are chosen to step down voltage from an eight NiMH battery pack — 11.2V max — to about 3.2V max. You may want to adapt these values according the battery pack you choose. Formula for voltage divider is : Vout = Vin * (R2 / (R1 + R2). In this case: 11.2 * (3.9 / (10 + 3.9)) = 3.14
	* For the voltage regulation unit:
		* One BY299 diode (2A diode)
		* One L78S05CV voltage regulator (2A 5V voltage regulator)
		* One 100 µF capacitor (to filter input voltage)
		* One 10 µF capacitor (to filter output voltage)
* Python (with Debian / Raspbian : packages “python” and “python-dev”)
* RPi.GPIO library (0.4.0a or newer) (with Debian / Raspbian : package “python-rpi.gpio”)

To help you with the assembly, you may refer to the following files :

* You may need to download and install [Raspberry Part](https://github.com/adafruit/Fritzing-Library/blob/master/AdaFruit.fzbz) for Fritzing
* picheckvoltage.fzz (into “doc” folder): the assembly mockup to open with Fritzing 
  ([http://fritzing.org/](http://fritzing.org/))


Electronic assembly
-------------------

Mockup on breadboard:
![Mockup on breadboard](/imgs/mockup.png "Mockup on breadboard")

Electronic schematics:
![Electronic schematics](/imgs/schematic.png "Electronic schematics")

Live install on [MovingRaspiPlus](https://github.com/aboudou/movingraspi)
![Live install on MovingRaspiPlus](http://farm9.staticflickr.com/8254/8666239532_48da91064d_c.jpg "Live install on MovingRaspiPlus")


How to use PiCheckVoltage
-------------------------

You'll first have to build the electronic assembly, then plug it to the Raspberry Pi

Then update "config.py" file to fit your needs. Each option is documented.

When you're done, just launch RasPiLEDmeter with `./picheckvoltage.sh start` as root user and that's all :-) When you want / need to stop it, just execute `./picheckvoltage.sh stop` as root user.

PiCheckVoltage provides a network interface to querie battery status through network. Just connect to it (default port is 50007), and status will be immediately sent, with the following format :

> \<low voltage ADC value\>|\<current voltage adc value\>|\<max voltage adc value\>||\<low voltage value\>|\<current voltage value\>|\<max voltage value\>

* Voltage ADC value is a number between 0 and 1023
* Voltage value is a number using Volt unit

An example return value could be : `731.332897319|853|975.110529758||8.4|9.3296875|11.2`, which means :

* ADC value for minimum battery voltage is around 731.
* ADC value for current voltage is 853.
* ADC value for maximum voltage is around 975.
* Minimum battery voltage is 8.4V.
* Current battery voltage is around 9.33V .
* Maximum battery voltage is 11.2V.

Note : ADC value for maximum voltage may not be equal to 1023 as we have to deal with the imprecision of the resistor voltage divider. With the given example, voltage reference for the ADC is 3.3V (+3.3V power line from Raspberry Pi), and the used resistor divider (10kΩ and 3.9kΩ resistors) steps down 11.2V to 3.14V, not speaking of resistor tolerance.
