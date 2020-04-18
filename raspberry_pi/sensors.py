# Import 3rd party modules
import grovepi
from grovepi import *
from grove_rgb_lcd import *

# Define constants and variables
# Digital input ports
# SIG,NC,VCC,GND
DHT_SENSOR_PORT = 8 # Temperature and Humidity sensor on D7
LIGHT_SENSOR = 0 # Light sensor on A0
DHT_SENSOR_TYPE = 0 #Input

# Set IO modes
grovepi.pinMode(LIGHT_SENSOR,"INPUT")

def read_light_sensor():
    return grovepi.analogRead(LIGHT_SENSOR)


def read_temperature_humidity():
    [temp, hum] = dht(DHT_SENSOR_PORT, DHT_SENSOR_TYPE)
    print(temp)
    return temp, hum