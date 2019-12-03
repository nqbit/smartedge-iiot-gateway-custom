#!/bin/sh
if [ ! -f /etc/apn.conf ]; then
   echo "/etc/apn.conf not found. Waiting for user configuration..."
   while [ ! -f /etc/apn.conf ]; do
           sleep 60
   done
   echo "APN is now configured..."
fi

ifconfig wwan0
if [ $? -eq 0 ]; then
   echo "Starting quectel service for APN $(cat /etc/apn.conf)"
   while true; do
           quectel-CM -s "$(cat /etc/apn.conf)"
           # Avoid trying to reconnect too often
           sleep 60
   done
else
   echo "Cellular modem wwan0 not found"
   # exit gracefully -- no modem installed..
fi
