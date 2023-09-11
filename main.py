# Import necessary libraries
import machine
import time
import utime
import math
import tm1637
import onewire
import ds18x20
from machine import ADC, Pin

# Initialize 7-segment display
display = tm1637.TM1637(clk=Pin(17), dio=Pin(18))

# Initialize DS18X20 temperature sensor
ds_pin = machine.Pin(16)  # DS18X20 Data Pin
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

# Initialize analog input (potentiometer)
analogue_input = ADC(Pin(26))

# Control pins for heater and pump
heater = Pin(9, Pin.OUT)
pump = Pin(10, Pin.OUT)

# Set initial display brightness and target temperature
display.brightness(0)
target_Cel = 28

# Scan for DS18X20 devices
roms = ds_sensor.scan()
print('Found a DS18X20 device')

while True:
    # Read the temperature setting from the potentiometer
    temperature_set = analogue_input.read_u16()
    aVr = 3.3 * float(temperature_set) / 65535
    aRt = 10000 * aVr / (3.3 - aVr)
    atemp = 1 / (((math.log(aRt / 10000)) / 3950) + (1 / (273.15 + 25)))
    set_Cel = math.floor(atemp - 273.15)

    # Convert temperature from DS18X20 sensor
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        Cel = math.floor(ds_sensor.read_temp(rom))

    # Check if the target temperature matches the set temperature
    if target_Cel == set_Cel:
        display.temperature(int(Cel))
        print("Reading: " + str(Cel) + " Set: " + str(set_Cel) + " Target: " + str(target_Cel))
        print("Displaying current temperature")
    else:
        print("Reading: " + str(Cel) + " Set: " + str(set_Cel) + " Target: " + str(target_Cel))
        if display_time < 400:
            # Display the set temperature
            display.temperature(set_Cel)
            utime.sleep_ms(200)
            display_time = display_time + 200
            print("Displaying set temperature")
        if display_time >= 400:
            # Update the target temperature
            target_Cel = set_Cel
            print("Displaying current temperature")

    # Control the heater and pump based on temperature difference
    if target_Cel <= Cel:   # Turn off heater and pump
        heater(0)
        pump(0)
        print("Heater and pump OFF")
    if (target_Cel - 5) > Cel:    # Turn on heater and pump
        heater(1)
        pump(1)
        print("Heaterand pump ON")
    utime.sleep_ms(200)