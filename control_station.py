#!/usr/bin/env python

# Script by Tanya Fish x
# Updates by Jaison Miller - jaison.miller@gmail.com

import sys
import time

import flotilla


print("""
...
""")

# Looks for the dock, and all of the modules we need
# attached to the dock so we can talk to them.

dock = flotilla.Client()
print("Client connected...")

while not dock.ready:
    pass

print("Finding modules...")
number = dock.first(flotilla.Number)
rainbow = dock.first(flotilla.Rainbow)
touch = dock.first(flotilla.Touch)
weather = dock.first(flotilla.Weather)

if number is None or rainbow is None or touch is None or weather is None:
    print("modules required not found...")
    dock.stop()
    sys.exit(1)
else:
    print("Found. Running...")
    
    # set the brightness
    number.set_brightness(100)
    tick = 0
    show = "time"

# Looks for a weather module and displays the temperature on the Number module
# Checks the pressure and shows it on the rainbow.

def set_mbar(value):
    pressure = 0
    try:
        pressure = float(value)/100

    except ValueError:
        raise TypeError("Value must be a number") 

    if pressure >= 999.5 or pressure < -99.5:
        number.set_string("Err")
        # raise ValueError("Number is too big: %d" % number)
    else:
        int_len = len(str(int(pressure // 1)))
        width = 4 - int_len // 3
        precission = 4 - int_len 
        # print("{} Pa".format(value))
        # print("{} mBar (float)".format(pressure))
        # print("{:{}.{}f} mBar".format(pressure, width, precission))
        number.set_string("{:{}.{}f} mBar".format(pressure, width, precission))

try:
    while True:
        time.sleep(0.5)
        number.update()
        tick = 1 - tick
        if show == "time":
            number.set_current_time(colon=tick)
        elif show == "temperature":
            number.set_temp(int(weather.temperature))
        elif show == "pressure":
            set_mbar(int(weather.pressure))
        else: 
            number.set_number(1234)
        if touch.one:
            print("ONE, time")
            number.set_string("time")
            number.update()
            time.sleep(1)
            show = "time"
        if touch.two:
            print("TWO, pressure")
            number.set_string(" hPa")
            number.update()
            time.sleep(1)
            show = "pressure"
        if touch.three:
            print("THREE, dunno")
            number.set_string("----")
            number.update()
            time.sleep(1)
            show = ""
        if touch.four:
            print("FOUR, temperature")
            number.set_string("temp")
            number.update()
            time.sleep(1)
            show = "temperature"


except KeyboardInterrupt:
    print("Stopping Flotilla...")
    dock.stop()
