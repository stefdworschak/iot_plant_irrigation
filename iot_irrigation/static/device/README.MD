# Instructions

## Requirements

- Python3
- Pip3
- IOT device running linux (e.g RaspberryPi)

## Download device setup from url

Go to "My Things" and click on the "Download Device Files" button

## Use scp (linux) or pscp (Windows using PuTTY) to copy the zip directory to your IoT device (RaspberryPI used here)

`scp ./{{thing_name}}.zip scp pi@raspberrypi.local:/home/pi`

or

`pscp ./{{thing_name}}.zip scp pi@raspberrypi.local:/home/pi`

## ssh into your device

Make sure your PC is on the same network as the device

`ssh pi@raspberrypi.local`

## Install 7z (zip utility tool)

`sudo apt-get install p7zip-full`

## Make a new folder for your project and cd into it

`mkdir {{thing_name}}`

or

`cd {{thing_name}}`

## Unzip your files

`sudo 7z x ~/{{thing_name}}.zip`

## Change the permissions for the keys folder

`sudo chmod 755 keys`

## Install requirements

`pip3 install -r requirements.txt`

or

`python3 -m pip install -r requirements.txt`
