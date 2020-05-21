import smbus
import time
import keyboard

# config bit to key
keysBA = { 0: 'up', 1: 'down', 2: 'left', 3: 'right', 4: 'left control', 5: 'left alt', 6: 'space', 7: 'left shift' }
keysBB = { 0: 'r',  1: 'f',    2: 'd',    3: 'g',     4: 'a',            5: 's',        6: 'q',     7: 'w' }
keysAA = { 0: 'z',  1: '1',    2: '5',    3: 0,       4: 0,              5: 'f2',       6: 'tab',   7: 'x' }
keysAB = { 0: 'i',  1: '2',    3: '6',    3: 0,       4: 'f2',           5: 0,          6: 0,       7: 'k' }

DEBUG = 0 # 1 for debug

def processKeys(input, old, keys):
  for bit in keys:
    # if false (0) the register is pulled down so is triggered
    # makeing a mask from bit
    mask = 1 << bit
    if (input & mask):
      # key release
      # if the key was pressed on the old input
      if not (old & mask):
        # then release the key
        keyboard.release(keys[bit])
        if (DEBUG): print "release "  + keys[bit] # print for debug
    else:
      # key press
      # if the key wasn't pressed on the old input (prevent double push)
      if (old & mask):
        # then push the key
        keyboard.press(keys[bit])
        if (DEBUG): print "press " + keys[bit] # print for debug

bus = smbus.SMBus(0)  # Rev 1 Pi uses 0, also if you are usin gert vga666 and bus 1 isn't usable
#bus = smbus.SMBus(1) # Rev 2 Pi uses 1

DEVICEA = 0x20 # Device address
DEVICEB = 0x21 # Device address
GPPUA = 0x0c # Pullup registers A
GPPUB = 0x0d # Pullap registers B
GPIOA  = 0x12 # Registers A
GPIOB = 0x13 # Registers B

# Set all GPs to input and PULLUP
# A0-A7
bus.write_byte_data(DEVICEA,GPPUA,0xff)
bus.write_byte_data(DEVICEB,GPPUA,0xff)
# B0-B7
bus.write_byte_data(DEVICEA,GPPUB,0xff)
bus.write_byte_data(DEVICEB,GPPUB,0xff)

oldAA = 255
oldAB = 255
oldBA = 255
oldBB = 255

# Loop until user presses CTRL-C
while True:

   # Read state of GPIOA and GPIOB on the both ports.
  readInputAA = bus.read_byte_data(DEVICEA,GPIOA)
  readInputAB = bus.read_byte_data(DEVICEA,GPIOB)
  readInputBA = bus.read_byte_data(DEVICEB,GPIOA) 
  readInputBB = bus.read_byte_data(DEVICEB,GPIOB)
  # Print for debug.
  if (DEBUG): print "Port 0x20: " + str(GPIOA) + " " + str(bin(readInputAA)) + " " + str(bin(readInputAB)) + " - Port 0x21: " + str(GPIOA) + " " + str(bin(readInputBA)) + " " + str(bin(readInputBB))
  # Processing inputs.
  processKeys(readInputAA, oldAA, keysAA)
  processKeys(readInputAB, oldAB, keysAB)
  processKeys(readInputBA, oldBA, keysBA)
  processKeys(readInputBB, oldBB, keysBB)
  # copy new inputs to old for compare.
  oldAA = readInputAA
  oldAB = readInputAB
  oldBA = readInputBA
  oldBB = readInputBB
