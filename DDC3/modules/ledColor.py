import os, machine, neopixel

ledPin = 8 # hardware pin that controls led
numLeds = 1 # number of leds (DDC3s only have 1)

# for compatibility with some prototypes still used by development team (will be phased out)
p0 = machine.Pin(0,machine.Pin.IN)
if(p0.value() == 0): 
    ledPin = 21

np = neopixel.NeoPixel(machine.Pin(ledPin), numLeds) # initialize led parameters

def ledColor(r, g, b):
    np[0] = (r,g,b) # prepare to turn led to specified color
    np.write() # send color to led
