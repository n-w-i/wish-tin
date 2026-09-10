# Step 0: is the board alive? No wiring at all -- just USB.
# XIAO ESP32S3 user LED is GPIO21 and is ACTIVE LOW (0 = on).
import time
from machine import Pin

led = Pin(21, Pin.OUT)
print("blinking 10x on GPIO21 -- watch the tiny orange LED next to the USB port")
for i in range(10):
    led.value(0)
    time.sleep_ms(120)
    led.value(1)
    time.sleep_ms(380)
    print("  blink", i + 1)
print("board is alive.")
