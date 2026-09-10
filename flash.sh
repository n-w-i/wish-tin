#!/bin/bash
# Erase and flash MicroPython. Only needed once.
# Put the XIAO in bootloader mode FIRST:
#   hold BOOT, tap RESET, release BOOT   (both tiny buttons by the USB port)
set -e
PORT="${1:-$(ls /dev/cu.usbmodem* 2>/dev/null | head -1)}"
[ -z "$PORT" ] && { echo "No board found. Plug it in, or pass the port explicitly."; exit 1; }
echo "Using $PORT"
esptool --chip esp32s3 --port "$PORT" erase-flash
esptool --chip esp32s3 --port "$PORT" --baud 921600 write-flash -z 0 firmware/ESP32_GENERIC_S3-v1.29.0.bin
echo
echo "Flashed. Tap RESET, then run: ./deploy.sh"
