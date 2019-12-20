#!/usr/bin/env python

from bottle import get, put, run, request, response, error, HTTP_CODES
import json
import os
import socket
import subprocess

from shutil import copyfile
from subprocess import call
from subprocess import PIPE, Popen
from time import sleep
import time, threading
import datetime
import configparser

def cmdline(command):
    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True
    )
    return process.communicate()[0]

#print(cmdline("sudo /opt/avnet-iot/iotservices/getid"))

Ssid_Signal = {
    "SSID": "SIGNAL",
    "SSID1": "SIGNA1L"
    }

Ssid_Signal.clear()


WIFI_IP_ADDRESS = '/tmp/ip_address'
IOTCONNECT_RUNNING = '/tmp/iotconnect.txt'

TEST_ADDRESS = ('avnet.iotconnect.io.', 443)
TEST_TIMEOUT = 10

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

def app_json(func):
    def inner(*args, **kwargs):
        response.content_type = 'application/json'
        # return json.dumps(func(*args, **kwargs), sort_keys=True, indent=4) + '\n'
        return json.dumps(func(*args, **kwargs))
    return inner

@put('/WiFiClientSSID_PSK')
def wificlient_ssid_psk():
    try:
        rsp = 1
        data = request.body.read()
        data = json.loads(data)
        for key, value in data.items():
            print(key)
            print(value)
            ssid = key 
            psk = value
        f = open("/etc/wpa_supplicant/wpa_supplicant.conf","w")
        f.write("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n")
        f.write("country=US\n")
        f.write("network={\n      key_mgmt=WPA-PSK")
        
        pskline = ("\npsk=" + "\"" + psk +"\"\n")
        
        f.write(pskline)
        ssidline = ("\nssid=" + "\"" + ssid + "\"\n")
        f.write(ssidline)
        f.write("\n }\n")
        f.close()
        os.system("/usr/bin/sudo /opt/avnet-iot/iotservices/wifi_connect >/dev/null 2>&1 &")
    except Exception as ex:
        print("Exception " + str(ex))
        os.system("/usr/bin/sudo ifconfig wlan0 down")
        time.sleep(float(10))
        os.system("/usr/bin/sudo ifconfig wlan0 up")
        rsp = 0

    return {'Response' : rsp }

@put('/CloudAttach')
def CloudAttach():
    try:
        rsp = 1
        os.system("/usr/bin/sudo /opt/avnet-iot/iotservices/wifi_client >/dev/null 2>&1 &")
    except:
        rsp = 0

    return {'Response' : rsp }


@put('/IOTNewCPID')
def newcpid():
    print("IOTNEWCPID")
    try:
        config = configparser.ConfigParser()

        config.read('/opt/avnet-iot/IoTConnect/sample/IoTConnectSDK.conf')
        rsp = 1
        data = request.body.readline()
        values = json.loads(data)
	config.set('CloudSDKConfiguration','cpid', values['cpid'])
	config.set('CloudSystemControl','username', values['username'])
	config.set('CloudSystemControl','password', values['password'])
#config['cpid'] = values['cpid']
	 
	with open('/opt/avnet-iot/IoTConnect/sample/IoTConnectSDK.conf', 'w') as configfile:    # save
            config.write(configfile)
	with open('/opt/avnet-iot/IoTConnect/sample/IoTConnectSDK.conf.default', 'w') as configfile:    # save
            config.write(configfile)
        # restart with new settings.
    except:
        rsp = -1

    return {'Response' : rsp }

@put('/WiFiAccessPointDisable')
def wifi_accesspoint_disable():
    try:
        rsp = 1
        # parse ssid/psk and do settings.
	os.system("/usr/bin/sudo /opt/avnet-iot/iotservices/wifi_connect_ignore &")
    except:
        rsp = 0
    return {'IsActive' : rsp }

@get('/DeviceId')
def device_id():
    
    try:
        dev_id = cmdline("sudo /opt/avnet-iot/iotservices/getid") 
        #socket.setdefaulttimeout(10)
        #host = socket.gethostbyname("www.google.com")
        #s = socket.create_connection((host, 80), 2)
        #s.close()
 
        print(dev_id)
        return {'DeviceId': dev_id}
    except:
        dev_id = '(unknown)'
    return {'DeviceId': dev_id}

@get('/SDKVersion')
def sdk_version():
    
    try:
        # Fix to use env var
        return {'SDKVersion': '1.1'}
    except:
        dev_id = '(unknown)'
    return {'DeviceId': dev_id}

@get('/GetSDKLog')
def get_sdk_log():
    try:
        os.system('tail -n 100 /home/avnet/iot.log >/tmp/result.log')
        with open('/tmp/result.log', 'r') as f:
            ret = f.read()
    except:
        ret = "Error"
    return {'GetSDKLog': ret}

@get('/IOTGetIOTConnectSDKConf')
def IOTGetIOTConnectConf():
    try:
        with open('/opt/avnet-iot/IoTConnect/sample/IoTConnectSDK.conf', 'r') as f:
            dev_id = f.read()
    except:
        dev_id = '(unknown)'
    return {'IOTGetIOTConnectSDKConf': dev_id}

@put('/IOTSetIOTConnectSDKConf')
def IOTSetIOTConnectConf():
    ret = 1
    try:
        with open('/opt/avnet-iot/IoTConnect/sample/IoTConnectSDK.conf', 'w') as f:
            data = request.body.read()
            f.write(data)
            f.close()
        with open('/opt/avnet-iot/IoTConnect/sample/IoTConnectSDK.conf.default', 'w') as f:
            data = request.body.read()
            f.write(data)
            f.close()
    except:
         ret = 0
    return {'IOTSetIOTConnectSDKConf': ret}

@put('/IOTSetAPNConf')
def IOTSetAPNConf():
    ret = 1
    try:
        with open('/etc/apn.conf', 'w') as f:
            data = request.body.read()
            f.write(data)
            f.close()
    except:
         ret = 0
    return {'IOTSetAPNConf': ret}

@get('/IOTGetIOTConnectSDKConfItem')
def IOTGetIOTConnectConfItem():
    ret = 1
    try:
        data = request.body.readline()
        print(data)   
        values = json.loads(data)
        for item in values:
            if (item == "SectionName"):
                section_name = values[item]
            if (item == "ValueName"):
		value_name = values[item]

        config = configparser.ConfigParser()
        config.read('/opt/avnet-iot/IoTConnect/sample/IoTConnectSDK.conf')
        print(config[section_name][value_name])
        ret_dict = {
            "SectionName":"Empty",
        }
	ret_dict["SectionName"] = section_name
        ret_dict[value_name] = config[section_name][value_name] 
    	print(ret_dict)
    except:
         ret_dict = {
             "SectionName":"Empty",
             "ValueName":"Empty"
         }
         print(ret_dict) 
    return {'IOTGetConnectSDKConfItem': ret_dict}

@put('/IOTSetIOTConnectSDKConfItem')
def IOTSetIOTConnectConfItem():
    ret = 1
    try:
        config = configparser.ConfigParser()

        config.read('/opt/avnet-iot/IoTConnect/sample/IoTConnectSDK.conf')
        data = request.body.readline()
        values = json.loads(data)
        print(data)
        print(values)
        for item in values:
            print(item)
            print(values[item])
            if (item == "SectionName"):
                section_name = values[item]
            else:
                section_value_name = item
                section_value_data = values[item]
        config.set(section_name, section_value_name, section_value_data)        
	 
	with open('/opt/avnet-iot/IoTConnect/sample/IoTConnectSDK.conf', 'w') as configfile:    # save
            config.write(configfile)
	with open('/opt/avnet-iot/IoTConnect/sample/IoTConnectSDK.conf.default', 'w') as configfile:    # save
            config.write(configfile)
    except:
         ret = 0
    return {'IOTSetConnectSDKConfItem': ret}

@get('/WiFiAccessPointList')
def wifi_list():
    try:
        Ssid_Signal.clear()
        essidnames = cmdline("sudo iwlist wlan0 scan | grep ESSID | cut -d ':' -f2 | tr -d '\"'")
        signalvalues = cmdline("sudo iwlist wlan0 scan | grep Quality | cut -d '=' -f3 ")
        name = essidnames.splitlines()
        sig = signalvalues.splitlines()
        count = essidnames.count('\n')
        count1 = signalvalues.count('\n')
        if (count > count1):
            count = count1 
        if (count == 0):
            Ssid_Signal["None Found"] = "-99 dBm"
            s = Ssid_Signal
            print(s)
            return {'WiFiAccessPointList': s}
        while(count !=0):
            Ssid_Signal[name[count - 1]] = sig[count - 1]
            count = count - 1 
        s = Ssid_Signal
    except Exception as ex:
        print("Exception" + str(ex))
        s = '(unknown)'
    print(s)
    return {'WiFiAccessPointList': s} 


@get('/NetworkStatus')
def network_status():
    connected = False
    try:
        socket.create_connection(TEST_ADDRESS, TEST_TIMEOUT).close()
        connected = True
    except:
        # For now assume connectivity
        connected = False 
    return {'IsConnected': connected}

@get('/WiFiClientConnectionStatus')
def wifi_client_connection_status():
    try:
	f = open(WIFI_IP_ADDRESS, 'r')
	addr = f.read()
    except:
        addr = '(unknown)'
    return {'WiFi client IP':addr}

@get('/WiFiGetIWLIST')
def wifi_get_iwlist():
    try:
	list = cmdline('sudo iwlist wlan0 scan')
    except:
        list = '(unknown)'
    return {'WiFiIWList':list}

@get('/WiFiGetWPAConf')
def wifi_get_wpa():
    try:
	f = open('/etc/wpa_supplicant/wpa_supplicant.conf', 'r')
	conf = f.read()
        print(conf)
    except:
        conf = '(unknown)'
    return {'WiFiWAPConf':conf}

@put('/WiFiSetWPAConf')
def wifi_set_wpa_conf():
    ret = 1
    try:
        data = request.body.read()
	f = open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w')
	f.write(data)
        print(data)
    except:
        ret = 0
    return {'Response':ret}
    
# TODO: How to decorate for *all* error responses?
# See: https://stackoverflow.com/a/51847982
@error(404)  # Not Found
@error(405)  # Method Not Allowed
@error(500)  # Internal server Error
@app_json
def error_response(error):
    return {
        'Error': response.status_code,
        'Text': HTTP_CODES.get(response.status_code, 'Unknown'),
        'Path': request.path,
        'Method': request.method
    }


if __name__ == '__main__':
    run(host='0.0.0.0', port=8080)
