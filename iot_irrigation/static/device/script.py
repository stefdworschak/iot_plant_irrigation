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
from copy import deepcopy

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

from sensors import (read_light_sensor, read_temperature_humidity, 
                    write_to_lcd, reset_lcd)
import keys

# State variables
publishing = True
listening = True
publishing_thread = None
listen_thread = None
terminate = False
watered_timestamp = None

# MQTT settings
BROKER_ADDRESS = os.environ.get('BROKER_ADDRESS', 'No value set')
BROKER_PORT = 8883
CLIENT_ID = os.environ.get('CLIENT_ID', 'No value set')
SUBSCRIBER_TOPIC = os.environ.get('SUBSCRIBER_TOPIC', 'No value set')
PUBLISHER_TOPIC = os.environ.get('PUBLISHER_TOPIC', 'No value set')

client = None

data_construct = {
    "state" : {
        "desired" : {},
        "reported" : {}
     }
}

def water_plant():
    """ Function for watering plants """
    global watered_timestamp
    watered_timestamp = datetime.now().isoformat()
    write_to_lcd("Watering of plants in progress")

    return


def last_message():
    """ Send a last response after disabling publishing or before closing the
    app in order to handle the callback on the client side

    Returns nothing """
    global client
    global watered_timestamp
    illuminance = read_light_sensor()
    temp, hum = read_temperature_humidity()
    watered_ts = watered_timestamp or datetime.now().isoformat()

    payload = {
        'timestamp': datetime.now().isoformat(),
        'type':'publish',
        'action': 'publishing',
        'data': {
            'illuminance': illuminance,
            'temperature': temp,
            'humidity': hum,
        },
        'watered_timestamp': watered_ts,
        'thing_id': CLIENT_ID,
        'publishing': False,
    }
    send_data = deepcopy(data_construct)
    send_data['state']['desired'] = payload
    send_data['state']['reported'] = payload
    client.publish(PUBLISHER_TOPIC, json.dumps(send_data), 0)
    return


def on_message(client, userdata, message):
    print('Message received=%s' % str(message.payload.decode('utf-8')))
    print('Message topic=%s' % (message.topic))
    global publishing
    global publishing_thread

    try:
        payload = json.loads(message.payload.decode('utf-8'))
        if payload.get('type') == 'listen':
            if payload.get('action') == 'water_plant':
                water_plant()
                return

            if payload.get('publishing'):
                if not publishing_thread.is_alive():
                    publishing = True
                    publishing_thread = Thread(target=publish)
                    publishing_thread.daemon = True
                    publishing_thread.start()
            else:
                last_message()
                publishing = False
                print("Not Publishing")
    except KeyError as key_error:
        print(f'A key error occurred: {key_error}')
        print(f'Payload data: {message.payload.decode("utf-8")}')
        print(f'For topic: {message.topic}')


def publish():
    """ Read all sensors and publish the results to the MQTT broker """
    print("Publishing Thread")
    global client
    global publishing
    while publishing:
        illuminance = read_light_sensor()
        temp, hum = read_temperature_humidity()
        watered_ts = watered_timestamp or datetime.now().isoformat()
        payload = {
            'timestamp': datetime.now().isoformat(),
            'type':'publish',
            'action': 'publishing',
            'data': {
                'illuminance': illuminance,
                'temperature': temp,
                'humidity': hum,
            },
            'watered_timestamp': watered_ts,
            'thing_id': CLIENT_ID,
            'publishing': True,
        }
        send_data = deepcopy(data_construct)
        send_data['state']['desired'] = payload
        send_data['state']['reported'] = payload
        client.publish(PUBLISHER_TOPIC, json.dumps(send_data), 0)
        print('Published readings: ', payload)
        time.sleep(10)
    print('Stop publishing.')


def listen(publisher):
    """ Listen for new messages on subscribed topic, start the publisher and

    """
    global client
    client.subscribe(SUBSCRIBER_TOPIC, 1, on_message)
    print('Subscribed to topic.')
    while listening:
        time.sleep(10)
    

def start_client(client_id):
    """ Start MQTT client, connect to broker, start the loop and set all
    required MQTT methods.

    """
    client = AWSIoTMQTTClient(client_id)
    # Configurations
    # For TLS mutual authentication
    client.configureEndpoint(BROKER_ADDRESS, BROKER_PORT)
    client.configureCredentials("keys/AmazonRootCA1.pem", "keys/private.pem.key", "keys/cert.pem.crt")
    client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    client.configureDrainingFrequency(2)  # Draining: 2 Hz
    client.configureConnectDisconnectTimeout(10)  # 10 sec
    client.configureMQTTOperationTimeout(5)  # 5 sec
    client.connect() 
    return client
    

def main():
    global publishing_thread
    global listen_thread
    global client
    client = start_client(CLIENT_ID)
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
        reset_lcd()
        break
