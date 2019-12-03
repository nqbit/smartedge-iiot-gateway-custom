#!/bin/bash
sleep 5

if [ ! -f /etc/apn.conf ]; then
  echo "/etc/apn.conf not found. Waiting for user configuration..."
  while [ ! -f /etc/apn.conf ]; do
      sleep 30
  done
  echo "APN is now configured..."
fi

echo "Starting quectel service for APN $(cat /etc/apn.conf)"
while true; do
    quectel-CM -s "$(cat /etc/apn.conf)"
    sleep 30
done &
