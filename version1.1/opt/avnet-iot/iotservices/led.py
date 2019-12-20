#!/usr/bin/env python

import json
import os
import socket
import subprocess

from subprocess import PIPE,Popen

from shutil import copyfile
from subprocess import call
from time import sleep
import time, threading
import datetime
def cmdline(command):
    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True
    )
    return process.communicate()[0]

ApMode = 0 
GreenThisTime = 0
RedThisTime = 0

WIFI_IP_ADDRESS = '/tmp/ip_address'
WiFiList = '/etc/WiFiAccessPointList'
IOTCONNECT_RUNNING = '/tmp/iotconnect.txt'
GREEN_LED ='/sys/class/leds/green/brightness'
RED_LED = '/sys/class/leds/red/brightness'

os.system('sudo chmod 666 /sys/class/leds/red/brightness')
os.system('sudo chmod 666 /sys/class/leds/green/brightness')


def green_led_on():
    os.system('echo 1 > /sys/class/leds/green/brightness')
    print("GON")
    sleep(0.2)

def green_led_off():
    os.system('echo 0 > /sys/class/leds/green/brightness')
    print("GOF")
    sleep(0.2)

def red_led_on():
    os.system('echo 1 > /sys/class/leds/red/brightness')
    print("RON")
    sleep(0.2)

def red_led_off():
    os.system('echo 0 > /sys/class/leds/red/brightness')
    print("ROF")
    sleep(0.2)

# TODO: Probably use '/etc/activated' or some other file that is
# created when the device is activated.
ACTIVATION_FILE = '/opt/avnet-iot/iotservices/device.txt'

# TODO: Need to change to 'avid....' at some point?
TEST_ADDRESS = ('avnet.iotconnect.io.', 443)
TEST_TIMEOUT = 4  # In seconds

# Use Station configuration files and restart daemons
def station_mode():
    return


# Use Access Point configuration files and restart daemons
def ap_mode():
    return

def check_switch():
    global GreenThisTime
    global RedThisTime
    while 1:
        global ApMode
        time.sleep(1)
	if ApMode == 1:
            if RedThisTime == 1:
                RedThisTime = 0
                red_led_off()
                green_led_on()
            else:
                RedThisTime = 1
                green_led_off()
                red_led_on()
        else:
            if GreeThisTime == 1:
                GreenThisTime = 0
                green_led_off()
            else:
                GreenThisTime = 1
                green_led_on()
                
                
def get_ap_mode():
    global ApMode
    active = 0
    try:
	hostapd = subprocess.call(['systemctl', 'is-active', 'hostapd.service'], stdout=FNULL, stderr=FNULL)
        if hostapd == 0:
            active = 1
            ApMode = 1
        else:
            ApMode = 0
    except Exception as ex:
        print(ex)
        ApMode = 0
        active = 0
    print("AP status" + str(active))
    return active

def check_network_status():
    while 1:
        try:
	    get_ap_mode()
        except Exception as ex:
            print(ex)
        time.sleep(TEST_TIMEOUT)

if __name__ == '__main__':
    print("Starting LED service")
    ApMode = 1 
    red_led_off()
    green_led_on()
    GreenThisTime = 1 
    t0 = threading.Thread(name='child procs', target=check_network_status)
    t0.start()
    t2 = threading.Thread(name='child procs', target=check_switch)
    t2.start()
    while 1:
        time.sleep(60*60)
    red_led_off()
    green_led_off()
