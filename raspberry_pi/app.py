#!/usr/bin/env python
"""
## License
The MIT License (MIT)
GrovePi for the Raspberry Pi: an open source platform for connecting Grove Sensors to the Raspberry Pi.
Copyright (C) 2017  Dexter Industries
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
# Import Python3 native modules
from datetime import datetime
import json
import os
import time
import sys
from threading import Thread

# Import 3rd party modules
import grovepi
from grovepi import *
from grove_rgb_lcd import *
import paho.mqtt.client as mqtt

# Import self-written custom modules
from dummy_data import generateRandom
import env_vars

# Define constants and variables
# Digital input ports
# SIG,NC,VCC,GND
DHT_SENSOR_PORT = 8 # Temperature and Humidity sensor on D7
LIGHT_SENSOR = 0 # Light sensor on A0
DHT_SENSOR_TYPE = 0 #Input

# Set IO modes
grovepi.pinMode(LIGHT_SENSOR,"INPUT")

# State variables
publishing = True
listening = True
publishing_thread = None
listen_thread = None
terminate = False

# MQTT settings
BROKER_ADDRESS = os.environ.get('BROKER_ADDRESS', 'No value set')
LISTEN_CLIENT_ID = os.environ.get('LISTEN_CLIENT_ID', 'No value set')
PUBLISH_CLIENT_ID = os.environ.get('PUBLISH_CLIENT_ID', 'No value set')
TOPIC = os.environ.get('TOPIC', 'No value set')
SUBSCRIBER = os.environ.get('SUBSCRIBER', 'No value set')

client = None


def read_light_sensor():
    # TODO: Enable actual functionality and remove random number generatore
    return grovepi.analogRead(LIGHT_SENSOR)
    #return generateRandom('illuminance')


def read_temperature_humidity():
    # TODO: Enable actual functionality and remove random number generatore
    [temp, hum] = dht(DHT_SENSOR_PORT, DHT_SENSOR_TYPE)
    print(temp)
    return temp, hum
    #return generateRandom('temperature'), generateRandom('humidity')


def last_message(client):
    """ Send a last response after disabling publishing or before closing the
    app in order to handle the callback on the client side

    Returns nothing """
    readings = {
        'pi1_timestamp': 0,
        'illuminance': read_light_sensor(),
        'raspberry_pi': 1,
        'publishing': False,
    }
    client.publish(TOPIC, json.dumps(readings))
    return


def on_message(client, userdata, message):
    print('Message received=%s' % str(message.payload.decode('utf-8')))
    print('Message topic=%s' % (message.topic))
    try:
        utf8_message = str(message.payload.decode('utf-8'))
        message = json.loads(utf8_message)
        global publishing
        global publishing_thread
        print(message)
        if message.get('terminate'):
            global terminate
            global listening
            listening = False
            publishing = False
            client.disconnect()
            client.loop_stop()
            terminate = True    

        if message.get('publishing'):
            publishing = True
            if not publishing_thread.is_alive():
                publishing_thread = Thread(target=publish)
                publishing_thread.daemon = True
                publishing_thread.start()
        else:
            # Send last reading before turning off to also change button
            last_message(client)
            publishing = False
            print("Not Publishing")
            
    except ValueError as value_error:
        print('The received message had an ill formed data object')
    except Exception as error:
        print('An error occurred')
        print(error)


def publish():
    """ Read all sensors and publish the results to the MQTT broker """
    print("Publishing Thread")
    client = start_client(PUBLISH_CLIENT_ID)
    while publishing:
        illuminance = read_light_sensor()
        temp, hum = read_temperature_humidity()
        readings = {
            'pi1_timestamp': datetime.now().isoformat(),
            'illuminance': read_light_sensor(),
            'temperature': temp,
            'humidity': hum,
            'raspberry_pi': 1
        }
        client.publish(TOPIC, json.dumps(readings))
        print('Published readings: ', readings)
        client.loop(.1)
        time.sleep(10)
    print('Stop publishing.')


def listen(publisher):
    """ Listen for new messages on subscribed topic, start the publisher and

    """
    client = start_client(LISTEN_CLIENT_ID)
    client.subscribe(SUBSCRIBER)
    print('Subscribed to topic.')
    while listening:
        client.loop(.1)
    

def start_client(client_id):
    """ Start MQTT client, connect to broker, start the loop and set all
    required MQTT methods.

    """
    client = mqtt.Client(client_id)
    client.connect(BROKER_ADDRESS)
    # Set all custom MQTT methods
    client.on_connect=on_connect
    client.on_publish=on_publish
    client.on_subscribe=on_subscribe
    client.on_message=on_message
    client.on_disconnect=on_disconnect
    client.on_socket_close=on_socket_close
    client.on_socket_unregister_write=on_socket_unregister_write 
    return client
    

def main():
    global publishing_thread
    global listen_thread
    publishing_thread = Thread(target=publish)
    publishing_thread.daemon = True
    listen_thread = Thread(target=listen, args=(publishing_thread,))
    listen_thread.daemon = True
    listen_thread.start() 

    while terminate == False:
        pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
