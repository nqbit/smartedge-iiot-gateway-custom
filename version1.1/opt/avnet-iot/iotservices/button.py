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

SwitchLong = 0
SwitchShort = 0
SwitchFactory = 0

def check_switch_short():
    global SwitchShort
    global SwitchLong
    global ShortSwitchDelay

    try:
    	while 1:
            print(cmdline("sudo cat /dev/button"))
            SwitchShort = 1
            print(SwitchLong)
	    print(SwitchFactory)
            # Psuedo debounce short press.
            #if (SwitchLong == 0):
            #    if (SwitchFactory == 0):
            print("SwitchShortActivated Resetting")
            print(cmdline("/usr/bin/sudo /opt/avnet-iot/iotservices/reboot"))
            time.sleep(1)
    except:
        print("Button Exception")

def check_switch_long():
    global SwitchLong
    global SwitchFactory

    try:
        while 1:
            print(cmdline("sudo cat /dev/reset"))
            print(SwitchLong)
            print(SwitchFactory)
            SwitchLong = 1
            if (SwitchFactory == 0):
                print("LongPress Resetting to Configuration State")
                print(cmdline("/usr/bin/sudo /opt/avnet-iot/iotservices/switch_only_configs"))
            time.sleep(1)
    except:
        print("Button Exception")
    
def check_switch_factory():
    global SwitchFactory

    try:
        while 1:
            print(cmdline("sudo cat /dev/resetfactory"))
            SwitchFactory = 1
            print("WARNING!!! LongPress Resetting to Factory State WARNING!!!")
            print(cmdline("/usr/bin/sudo /opt/avnet-iot/iotservices/switch_only"))
            time.sleep(1)
    except:
        print("Button Exception")


if __name__ == '__main__':
    time.sleep(2)
    print("Starting button service")
    t = threading.Thread(name='child procs', target=check_switch_long)
    t.start()
    t1 = threading.Thread(name='child procs', target=check_switch_short)
    t1.start()
    t2 = threading.Thread(name='child procs', target=check_switch_factory)
    t2.start()
    cmdline('sudo chmod 666 /dev/watchdog1')
    cmdline('echo V | sudo tee >/dev/watchdog1')
    while 1:
        time.sleep(60*60)
    #run(host='0.0.0.0', port=8080)
