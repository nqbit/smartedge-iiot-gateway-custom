#!/bin/bash

echo "Starting quectel service for APN $(cat /etc/apn.conf)"
quectel-CM -s "$(cat /etc/apn.conf)"
