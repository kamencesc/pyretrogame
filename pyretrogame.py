# -----------------------------------------------
# Basic conversion form retrogame from Adafruit
# in python.
# ONLY FOR MCP23017 I/O EXPANDERS
# 
# retrogame.cfg compatible
#
# By Francesc Bofill
# twitter: @kamencesc
#
# ------------------------------------------------

import smbus
import sys
#import time # default disabled, maybe is needed a time.sleep(1/1000000.0) at the end of each loop
import keyboard

# A dictonary to change reference from original retrogame keytable
modDict = {'LEFTSHIFT': 'left shift', 'RIGHTCTRL': 'right ctrl', 'RIGHTALT': 'right alt', 'RIGHTSHIFT': 'right shift', 'LEFTALT': 'left alt', 'LEFTCTRL': 'left ctrl'}

DEBUG = 0 # 1 for debug
busNum = 0 # Default bus is 1, 0 for old RPI and if you are using alternative I2C ports
cfgFile = "/boot/retrogame.cfg"

# Get arguments for manual config
numarg = len(sys.argv)
for n in range(numarg):
  if (sys.argv[n].upper() == "DEBUG"):
    DEBUG = int(sys.argv[n+1])
  elif (sys.argv[n].upper() == 'BUS'):
    busNum = int(sys.argv[n+1])
  elif (sys.argv[n][-3:len(sys.argv[n])].upper() == 'CFG'):
    cfgFile = sys.argv[n]

# Process the input to press an release keys
def processKeys(inputDict, keys):
  for dev in keys: # for each device
    newInput = inputDict[dev]
    oldInput = inputDict[0x100 + dev]
    for bit in keys[dev]:
      # if false (0) the register is pulled down so is triggered
      # makeing a mask from bit
      mask = 1 << bit
      if (newInput & mask):
        # key release
        # if the key was pressed on the old input
        if not (oldInput & mask):
          # then release the key
          keyboard.release(keys[dev][bit])
          if (DEBUG): print "Release "  + keys[dev][bit] # print for debug
      else:
        # key press
        # if the key wasn't pressed on the old input (prevent double push)
        if (oldInput & mask):
          # then push the key
          keyboard.press(keys[dev][bit])
          if (DEBUG): print "Press " + keys[dev][bit] # print for debug

# Create an empty keyDict
def emptyKeyDict():
  tempDict = {}
  for x in range(0,8):
    tempDict.update({x: 0})
  return tempDict

# Set all registrers to PULLUP
def setPullUp(device, tempbus):
  GPPUA = 0x0c # Pullup registers A
  GPPUB = 0x0d # Pullap registers B
  tempbus.write_byte_data(device,GPPUA,0xff) #A0-A7
  tempbus.write_byte_data(device,GPPUB,0xff) #B0-B7

# Read the A0-A7 and B0-B7 from a DEVICE
def readAll( DEVICE, tempbus ):
  GPIOA = 0x12
  GPIOB = 0x13
  tempDict = {}
  readInputA = tempbus.read_byte_data(DEVICE,GPIOA)
  readInputB = tempbus.read_byte_data(DEVICE,GPIOB)
  tempDict = { DEVICE: (readInputB<<8) | readInputA}
  return tempDict

# create empty Dictionaries
keyDict = {}
readInput = {}

# Read Config File
if (DEBUG): print "Opening config file: " + cfgFile
f = open(cfgFile,'r')
for l in f:
  line = l.strip()
  if len(line):
    if not (line[0] == '#'): # if not a comment line
      if (line[0:3].upper() == "BUS"): # Set manual bus number
        splitLine=line.split()
        busNum = int(splitLine[1])
      if not (line[0:3].upper() == "IRQ"): # not needed the IRQ, we read directly and get the port from cfg
        splitLine=line.split()
        # 0 = key    1 = pin number
        keyRef = splitLine[0] # key
        pinNumber = int(splitLine[1]) # pin number
        devicePort = (( pinNumber -32) / 16) + 32 # get the device port (0x20....)
        regNumber = pinNumber % 16 # get the register number in the MCP23017
        if not devicePort in keyDict: # if it's a new device in the cfg then create empty dict
          emptyDict = emptyKeyDict()
          keyDict.update({ devicePort: emptyDict})
        tempKeyDict = keyDict[devicePort] # get the dictionary of this device
        # change the values from retrogame keytable to out keytable
        if keyRef in modDict:
          keyRef = modDict[keyRef]
        tempKeyDict.update({ regNumber: keyRef.lower()}) # add the key
        if (DEBUG): print "PIN " + str(pinNumber) + " to key " + splitLine[0] + " \ " + keyRef.lower()
        keyDict.update({devicePort: tempKeyDict}) # update Keys Dictionary
f.close() #close config file

if (DEBUG): print "Opening bus " + str(busNum)
bus = smbus.SMBus(busNum)

# Set all registers in the usable device to PULLUP
for n in keyDict:
  setPullUp(n, bus)

# set initial new and old readInput to 1
for i in keyDict:
  # Dictonary contents new input (0x20) and old input (0x120)
  readInput.update({ i: 0b1111111111111111, 0x100 + i: 0b1111111111111111})

# Loop until user presses CTRL-C
if (DEBUG): print "Starting Loop"
while True:

  # Read state of GPIOA and GPIOB on the both ports.
  for i in keyDict:
    if i <= 0x100: # only change the new inputs
      readInput.update( readAll(i, bus) )

  # Processing inputs.
  processKeys(readInput, keyDict)

  for i in keyDict:
    readInput.update({0x100 + i: readInput[i]})

  #time.sleep(1/100.0) #sleep 1us
