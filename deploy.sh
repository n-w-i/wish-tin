#!/bin/bash
# Copy the tin onto the board and restart it.
set -e
mpremote cp ssd1306.py scenes.py quotes.py main.py :
echo "copied. opening console (ctrl-] to exit)"
mpremote reset
sleep 1
mpremote repl
