#!/bin/bash
sleep 5
#!/bin/bash

if [ ! -f /etc/apn.conf ]; then
  echo "/etc/apn.conf not found. Waiting for user configuration..."
  while [ ! -f /etc/apn.conf ]; do
      sleep 60
  done
  echo "APN is now configured..."
fi

echo "Starting quectel service for APN $(cat /etc/apn.conf)"
quectel-CM -s "$(cat /etc/apn.conf)"

