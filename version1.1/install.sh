#!/bin/bash
installdir=$(echo $(pwd)|tr -d '\r')
echo $installdir
echo "Upgrading raspberry pi and installing IoTConnect SDK please wait."
if [ -z "$1" ]; then
    echo "May specify useoldsdk or importoldsdk (./install.sh useoldsdk)"
fi


# put on hold updates in boot/kernel area (Note: Check for buster, jessie, etc.)
sudo apt-mark hold raspberrypi-bootloader
sudo apt-mark hold raspberrypi-kernel
sudo apt-mark hold raspberrypi-sys-mods

# fix problem with unattended operation.  Release when were done.
sudo apt-mark hold apache2
sudo apt-mark hold php
sudo cp -f $intstalldir/etc/apt/apt.conf.d/71debconf /etc/apt/apt.conf.d/71debconf
echo "Apt update"
sudo apt-get -y update

# install missing packages
echo "Install additional packages"
sudo apt-get -y install hostapd
sudo apt-get -y install dnsmasq
sudo apt-get -y install dnsutils
sudo apt-get -y install pydb
sudo pip install psutil
sudo pip install pyserial
sudo pip install minimalmodbus
sudo pip install pyudev
sudo pip install pyusb
sudo pip install usbinfo
sudo pip install ifaddr
sudo pip install bitstruct

sudo apt-get -y install anacron
sudo apt-get -y install busybox
sudo apt-get -y install nmap
sudo apt-get -y install udhcpc
sudo apt-get -y install dnsutils

# Install quectel package
echo "Enabling cell modem quectel system"
sudo gunzip quectel.tar.gz
sudo tar -xvf quectel.tar
sudo .quectel/updates/install.sh

# copy over new sdk files
echo "Copying new SDK"
sudo mkdir /opt
sudo mkdir /opt/avnet-iot

sudo cp -Rf $installdir/opt/avnet-iot/* /opt/avnet-iot/
#uninstall old IOTSDK
sudo pip uninstall -y iotconnect-sdk-py2.7
#install new IOTSDK


pushd /opt/avnet-iot/IoTConnect/packages
sudo pip install iotconnect-sdk-py2.7-2.0.tar.gz
sudo rm /sbin/reboot
sudo ln -s /opt/annet-iot/iotservices/reboot /sbin/reboot
sudo ln -s /opt/avnet-iot/services/attinyupdate.service /etc/systemd/system/attinyupdate.service
sudo ln -s /opt/avnet-iot/services/bootservice.service /etc/systemd/system/bootservice.service
sudo ln -s /opt/avnet-iot/services/smartedgehalt.service /etc/systemd/system/smartedgehalt.service
popd
sudo cp -R $installdir/etc/* /etc
# new bootloader
sudo cp $installdir/boot/kernel7.img /boot
sync
# quickly swap out ATTiny drivers.
sudo killall python
sudo killall cat
sudo rmmod mcp251x
sudo rmmod attiny_led
sudo rmmod attiny_btn
sudo rmmod attiny_wtd
sudo rmmod attiny_mfd
sudo cp -R $installdir/lib/* /lib
sync
# reload and stop watchdog
sudo modprobe attiny_mfd
sudo modprobe attiny_btn
sudo modprobe attiny_led
sudo modprobe attiny_wtd

# reload system services
sudo systemctl daemon-reload
sudo systemctl enable bootservice
sudo systemctl enable ledservice
sudo systemctl enable buttonservice
sudo systemctl enable restservice
sudo systemctl enable watchdogstop

#read -p "Press a key"
# change to enviroment variable
if [ "$1" == "importsdk" ]; then
    echo "Using version 1.0 SDK imports"
    sudo cp -f /opt/avnet-iot/IoTConnect/sample/user_functions.py /opt/avnet-iot/IoTConnect/sample/user_functions.py.version1_1
    sudo cp -f /usr/bin/IoTConnectSDK_Py2.7_Testing/sample/user_functions.py /opt/avnet-iot/IoTConnect/sample/user_functions.py
    sudo cp -f /opt/avnet-iot/IoTConnect/sample/IoTConnectSDK.conf /opt/avnet-iot/IoTConnect/sample/IoTConnectSDK.conf.version1_1
    sudo cp -f /usr/bin/IoTConnectSDK_Py2.7_Testing/sample/IoTConnectSDK.conf /opt/avnet-iot/IoTConnect/sample/IoTConnectSDK.conf
elif [ "$1" == "useoldsdk" ]; then
    echo "Using version 1.0 SDK as is"
    sudo cp -f /opt/avnet-iot/IoTConnect/sample/user_functions.py /opt/avnet-iot/IoTConnect/sample/user_functions.py.version1_1
    sudo cp -f /usr/bin/IoTConnectSDK_Py2.7_Testing/sample/user_functions.py /opt/avnet-iot/IoTConnect/sample/user_functions.py
    sudo cp -f /opt/avnet-iot/IoTConnect/sample/IoTConnectSDK.conf /opt/avnet-iot/IoTConnect/sample/IoTConnectSDK.conf.version1_1
    sudo cp -f /usr/bin/IoTConnectSDK_Py2.7_Testing/sample/IoTConnectSDK.conf /opt/avnet-iot/IoTConnect/sample/IoTConnectSDK.conf
    sudo cp -f /opt/avnet-iot/IoTConnect/sample/example.py /opt/avnet-iot/IoTConnect/sample/example.py.version1_1
    sudo cp -f /usr/bin/IoTConnectSDK_Py2.7_Testing/sample/example.py /opt/avnet-iot/IoTConnect/sample/example.py
else
    echo "Using version 1.1 SDK"
fi

sudo cp /etc/default/hostapd.ap /etc/default/hostapd
sudo cp /etc/dhcpcd.conf.ap /etc/dhcpcd.conf
sudo cp /etc/dnsmasq.conf.ap /etc/dnsmasq.conf
sudo systemctl daemon-reload
sudo systemctl disable iotconnectservice
sudo systemctl stop iotconnectservice
sudo systemctl enable restservice
sudo systemctl enable hostapd.service
sudo systemctl enable dnsmasq.service
sudo systemctl start hostapd.service
sudo systemctl start dnsmasq.service
sudo systemctl restart dhcpcd.service
# release hold on apache2.
sudo apt-mark unhold apache2
sudo apt-mark unhold php
echo "Rebooting with version 1.1"
sudo rm /sbin/reboot
sudo ln -s /bin/systemctl /sbin/reboot

if [ ! -f /usr/local/bin/tpm2_pcrlist ]; then
    echo "Installing TPM2 components please wait."
    sudo ./tpm/tpm2_setup.sh
fi

sudo /opt/avnet-iot/iotservices/cleanup






