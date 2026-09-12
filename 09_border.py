# Holds a border around the full 128x64 lit area, for sizing a bezel.
# Corner ticks mark the exact extents. Runs until you unplug it.
import time
from machine import Pin, I2C, SoftI2C
from ssd1306 import SSD1306_I2C

try:
    i2c = I2C(0, sda=Pin(5), scl=Pin(6), freq=400000)
except Exception:
    i2c = SoftI2C(sda=Pin(5), scl=Pin(6), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)
oled.contrast(255)

oled.fill(0)
oled.rect(0, 0, 128, 64, 1)          # exact edge of the lit area
for x, y in ((0, 0), (127, 0), (0, 63), (127, 63)):
    oled.fill_rect(max(x - 3, 0), max(y - 3, 0), 4, 4, 1)   # corner blocks
oled.hline(0, 32, 128, 1)            # centre lines, for centring the window
oled.vline(64, 0, 64, 1)
oled.text("128x64", 40, 20, 1)
oled.show()
print("border held. active area is 128x64 px, about 22 x 11 mm.")
print("unplug and replug when you're done to get the ceremony back.")
