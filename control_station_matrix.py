#!/usr/bin/env python

# Script by Tanya Fish x
# Updates by Jaison Miller - jaison.miller@gmail.com

import sys
import time
import datetime
import numpy
import sqlite3
import flotilla


print("""
...
""")

# Looks for the dock, and all of the modules we need
# attached to the dock so we can talk to them.

# Create / connect to database
print("Setting up the weather database")
conn = sqlite3.connect('weather_info.db')
curs = conn.cursor()

# get the list of existing tables:
curs.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='weather_data' ''')

print('''
        >>>
        ''')

if curs.fetchone()[0] == 1: 
    print('weather_data exists - adding data to it')
else:
    print("table doesn't exist - creating weather_data")
    curs.execute(''' CREATE TABLE weather_data
                        (record_date text, pressure_pa real, temperature_celsius real) ''')

print('''
        <<<
        ''')

conn.commit()

dock = flotilla.Client()
print("Client connected...")

while not dock.ready:
    pass

print("Finding modules...")
number = dock.first(flotilla.Number)
rainbow = dock.first(flotilla.Rainbow)
touch = dock.first(flotilla.Touch)
weather = dock.first(flotilla.Weather)
matrix = dock.first(flotilla.Matrix)
matrix.set_brightness(50)

buf = None

if number is None or rainbow is None or touch is None or weather is None or matrix is None:
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

def grow_values(values, new_value):
    # setup the empty values for the graph plot

    # insert a new value at the beginning    
    values.insert(0, new_value)
    
    # get rid of the last value keeping the list at 7 items
    values = values[:7]
    
    return values

def set_graph(values, low=None, high=None, x=0, y=0, width=None, height=None, brightness=1.0):
    """Plot a series of values into the display buffer."""
    global buf

    if width is None:
        width = 7

    if height is None:
        height = 7

    if low is None:
        low = min(values)

    if high is None:
        high = max(values)

    buf = grow_buffer(x + width, y + height)

    span = high - low

    for p_x in range(width):
        try:
            value = values[p_x]
            value -= low
            value /= float(span)
            value *= height * 10.0

            value = min(value, height * 10)
            value = max(value, 0)

            for p_y in range(height):
                b = brightness
                if value <= 10:
                    b = (value / 10.0) * brightness

                matrix.set_pixel(x + p_x, y + (height - p_y), b)
                # print("x = {}, y = {}, b = {}".format(x + p_x, y + (height - p_y), b))
                value -= 10
                if value < 0:
                    value = 0

        except IndexError:
            return

def grow_buffer(x, y):
    """Grows a copy of the buffer until the new shape fits inside it.
    :param x: Minimum x size
    :param y: Minimum y size
    """
    x_pad = max(0, x - buf.shape[0])
    y_pad = max(0, y - buf.shape[1])
    return numpy.pad(buf, ((0, x_pad), (0, y_pad)), 'constant')

try:
    values = [0] * 7
    buf = numpy.zeros((7, 7))
    while True:
        time.sleep(1)
        now = datetime.datetime.now()
        current_second = now.strftime("%S")
        number.update()
        matrix.update()

        if current_second == "00":
            print('''
            Update: weather_data 
            ''')
            print('record_date: {:%Y-%m-%dT%H:%M:%S}'.format(now))
            print('pressure_pa: {}'.format(weather.pressure*10))
            print('temperature_celsius: {}'.format(weather.temperature))

            curs.execute(''' INSERT INTO weather_data VALUES ('{:%Y-%m-%dT%H:%M:%S}', '{}', '{}')'''.format(now, weather.pressure*10, weather.temperature))
            conn.commit()

        # print(matrix.pp())
        tick = 1 - tick
        if show == "time":
            number.set_current_time(colon=tick)
        elif show == "temperature":
            number.set_temp(int(weather.temperature))
            if current_second == "00":
                values = grow_values(values, int(weather.temperature))
                # print(values)
                set_graph(values, high=29, low=21)
        elif show == "pressure":
            set_mbar(int(weather.pressure))
            if current_second == "00":
                values = grow_values(values, int(weather.pressure))
                set_graph(values, high=10100, low=8000)
        else: 
            number.set_number(1234)
            matrix.clear()
        if touch.one:
            print("ONE, time")
            number.set_string("time")
            number.update()
            time.sleep(1)
            show = "time"
        if touch.two:
            print("TWO, pressure")
            number.set_string(" kPa")
            number.update()
            time.sleep(1)
            show = "pressure"
            values = [0] * 7
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
            values = [0] * 7


except KeyboardInterrupt:
    print("Stopping Flotilla...")
    dock.stop()
    if conn:
        print("Closing the database connection...")
        conn.close()
