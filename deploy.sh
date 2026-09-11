#!/bin/bash
# Copy the tin onto the board and restart it. main.py runs on boot.
set -e
mpremote cp ssd1306.py scenes.py quotes.py main.py :
mpremote reset
echo "deployed. press the button."
echo "to watch the console:  mpremote repl   (ctrl-] to exit)"
