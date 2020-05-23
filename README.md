# pyretrogame

Basic python conversion from Adafruit's retrogame (https://github.com/adafruit/Adafruit-Retrogame)

Needs keybaord module from boppeh ([https://github.com/boppreh/keyboard](https://github.com/boppreh/keyboard)). You can find more information in his github and how to install it. The use of pip is recomendable.

## How to use
Call it from terminal with sudo:

    sudo python pyretrogame.py

You can add new path for cfg file and change some options (read below):

    sudo python /path/to/newcfg.cfg bus 0

Add to your /etc/rc.local file to launch at system strartup with " &" at the end of the line (and change to your original location):

    sudo python /home/pi/pyretrogame/pyretrogame.py &
    
My recomendation is to add this line if you are familiar with screen:

    screen -dmS pyretrogame sudo python /home/pi/pyretrogame/pyretrogame.py debug 1

With this you can acces to this screen via ssh and with this command:

    screen -r pyretrogame

And there you can see all debug text.

## Differences
You can change from bus 1 to 0 by editing a variable on the py file
There's some difference between the projects, it only works on additional MCP23017 I/O Extender (8 of them), so the 0-31 pins from Raspberry PI GPIO doesn't work.

IRQ map doesn't needed! You don't need to pin INTA to a GPIO pin, it works without it, IRQ config from cfg is discarded. Oh! Yes, your retrogame.cfg in /boot/retrograme.cfg will work!

Not all keys are mapped (e.g. windows key), so maybe some keys don't work, it's based on keyboard library from boppeh. But you can still use the retrogame keytable in the cfg file.

Configurable from command line!

As the original one, you can pass as a parameter a new path to your cfg file, /boot/retrogame.cfg is the default path.

bus [0/1]: you can select the bus to read MCP23017, bus 1 is the default bus on the new Raspberry Pi (+512mb ram version), but the new ones still have the second I2C port (pin 27 & 28), so you can use this port if you have the gert VGA666 in your GPIO (that uses pin 3 & 5 for implementation).

debug [0/1]: 0 = default, there's nothing on the command line. 1 for for basic debug info as key press and release.

## FYI
I used a lvl shifter with the SDA and SCL pins and it works like a charm, but it's because my MCP23017 ara powered directly from 5v power source. If you power them from the 3v3 pin you don't need the lvl shifter.
