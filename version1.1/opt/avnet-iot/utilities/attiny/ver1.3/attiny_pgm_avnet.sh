#!/bin/bash

ZIPFILE="$1"

# Exit with error if we are not root
if [[ "$(id -u)" != "0" ]]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

function extract_image_file ()
{
  unzip -o "$ZIPFILE"
}

if [ $# -lt "1" ]; then
  echo "Usage: Please specify zip file containing the customer image"
  exit 1
fi

if [ ! -f "$ZIPFILE" ]; then
  echo "Error: $ZIPFILE not found"
  exit 2
fi

# Verify zip has one file and record its length
regex="([A-Za-z0-9._%+-]+)\s+[-]+\s+[-]+\s+([0-9]+)\s+([0-9]+) file.?$"

zipfilelist=$(unzip -l $ZIPFILE)

if [ $? -ne 0 ]; then
  echo "$ZIPFILE does not appear to be a valid zipfile"
  exit 3
else
  if [[ $zipfilelist =~ $regex ]]; then
    FILE_NAME="${BASH_REMATCH[1]}"
    IMAGE_SIZE_IN_BYTES="${BASH_REMATCH[2]}"
    NUM_ZIP_FILES="${BASH_REMATCH[3]}"
  else
    echo "Error: Unexpected Zip file listing output"
    echo $zipfilelist
    exit 4
  fi
fi

extract_image_file

gpio_base=208
mcu_spi_cs=$((gpio_base+0))
mcu_resetn=$((gpio_base+1))
failed=0

if [ ! -d /sys/class/gpio/gpio${mcu_spi_cs} ]; then echo "${mcu_spi_cs}" | sudo tee "/sys/class/gpio/export" 1> /dev/null 2> /dev/null; fi

echo high | sudo tee "/sys/class/gpio/gpio${mcu_spi_cs}/direction" 1> /dev/null 2> /dev/null
echo 1 | sudo tee "/sys/class/gpio/gpio${mcu_spi_cs}/value" 1> /dev/null 2> /dev/null

#load dtoverlay for ATtiny
result=$(sudo dtoverlay avnet-iot-mcu.dtbo)

if [ $? -ne 0 ]; then
  echo "Could not load overlay to write to ATtiny"
  echo $result
  failed=1
else
  sleep 1

result=$(sudo ./avrdude -q -p attiny88 -C avrdude_working.conf -c avnet_iot_spi -P /dev/spidev2.2:/dev/gpiochip4:1 -v -U flash:w:$FILE_NAME:i 2>&1 /dev/null)

  if [ $? -ne 0 ]; then
    #retry once
    result=$(sudo ./avrdude -q -p attiny88 -C avrdude_working.conf -c avnet_iot_spi -P /dev/spidev2.2:/dev/gpiochip4:1 -v -U flash:w:$FILE_NAME:i 2>&1 /dev/null)

    if [ $? -ne 0 ]; then
      echo "Programming Failed! Review output for errors."
      echo $result
      failed=1
    fi
  fi
fi

#remove overlay for ATtiny
sudo dtoverlay -R avnet-iot-mcu

if [ ! -d /sys/class/gpio/gpio${mcu_resetn} ]; then echo "${mcu_resetn}" | sudo tee "/sys/class/gpio/export" 1> /dev/null 2> /dev/null; fi

echo high | sudo tee "/sys/class/gpio/gpio${mcu_resetn}/direction" 1> /dev/null 2> /dev/null
echo 1 | sudo tee "/sys/class/gpio/gpio${mcu_resetn}/value" 1> /dev/null 2> /dev/null


echo 0 | sudo tee "/sys/class/gpio/gpio${mcu_spi_cs}/value" 1> /dev/null 2> /dev/null

echo "${mcu_spi_cs}" | sudo tee "/sys/class/gpio/unexport" 1> /dev/null 2> /dev/null
echo "${mcu_resetn}" | sudo tee "/sys/class/gpio/unexport" 1> /dev/null 2> /dev/null

if [ $failed == 0 ]; then
  echo "Passed - ATtiny programming"
  exit 0
else
  echo "Failed - ATtiny programming"
fi

exit 20
