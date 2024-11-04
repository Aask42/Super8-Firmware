# boot.py
from machine import I2C, Pin
import time

PETAL_ADDRESS = 0x00
TOUCHWHEEL_ADDRESS = 0x54

# Testing options
bootLED = Pin("LED", Pin.OUT)
bootLED.on()

# Button definitions
buttonA = Pin(8, Pin.IN, Pin.PULL_UP)
buttonB = Pin(9, Pin.IN, Pin.PULL_UP)
buttonC = Pin(28, Pin.IN, Pin.PULL_UP)

# GPIO definitions
gpio11 = Pin(7, Pin.OUT)
gpio12 = Pin(6, Pin.OUT)
gpio21 = Pin(5, Pin.OUT)
gpio22 = Pin(4, Pin.OUT)
gpio31 = Pin(3, Pin.OUT)
gpio32 = Pin(2, Pin.OUT)
gpio41 = Pin(22, Pin.OUT)
gpio42 = Pin(21, Pin.OUT)
gpio51 = Pin(20, Pin.OUT)
gpio52 = Pin(19, Pin.OUT)
gpio61 = Pin(18, Pin.OUT)
gpio62 = Pin(17, Pin.OUT)

GPIOs = [[gpio11, gpio12], [gpio21, gpio22], [gpio31, gpio32], [gpio41, gpio42], [gpio51, gpio52], [gpio61, gpio62]]

# Initialize I2C peripherals
i2c0 = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
i2c1 = I2C(1, sda=Pin(26), scl=Pin(27), freq=400_000)

def which_bus_has_device_id(i2c_id, debug=False):
    i2c0_bus = i2c0.scan() 
    if debug:
        print("Bus 0: ", [hex(x) for x in i2c0_bus])
    
    i2c1_bus = i2c1.scan()
    if debug:
        print("Bus 1: ", [hex(x) for x in i2c1_bus])

    busses = []
    if i2c_id in i2c0_bus:
        busses.append(i2c0)
    if i2c_id in i2c1_bus:
        busses.append(i2c1)

    return busses

def petal_init(bus):
    bus.writeto_mem(PETAL_ADDRESS, 0x09, bytes([0x00]))  # Raw pixel mode
    bus.writeto_mem(PETAL_ADDRESS, 0x0A, bytes([0x09]))  # Intensity level
    bus.writeto_mem(PETAL_ADDRESS, 0x0B, bytes([0x07]))  # Enable all segments
    bus.writeto_mem(PETAL_ADDRESS, 0x0C, bytes([0x81]))  # Undo shutdown
    bus.writeto_mem(PETAL_ADDRESS, 0x0D, bytes([0x00]))
    bus.writeto_mem(PETAL_ADDRESS, 0x0E, bytes([0x00]))  # No special features
    bus.writeto_mem(PETAL_ADDRESS, 0x0F, bytes([0x00]))  # Turn off test mode
petal_bus = None
try:
    petal_init(i2c0)
    petal_bus = i2c0
except: 
    pass
try:
    petal_init(i2c1)
    petal_bus = i2c1
except:
    pass
if not petal_bus:
    print(f"Warning: Petal not found.")

