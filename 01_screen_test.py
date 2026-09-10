# Step 1: is the OLED wired correctly?
# Wire only these four before running:
#   OLED VCC -> 3V3   OLED GND -> GND   OLED SDA -> D4   OLED SCL -> D5
from machine import Pin, I2C, SoftI2C
import time

SDA, SCL = 5, 6          # XIAO ESP32S3 D4 / D5

try:
    i2c = I2C(0, sda=Pin(SDA), scl=Pin(SCL), freq=400000)
except Exception:
    i2c = SoftI2C(sda=Pin(SDA), scl=Pin(SCL), freq=400000)

found = i2c.scan()
print("I2C scan:", [hex(a) for a in found])

if not found:
    print()
    print("Nothing on the bus. In order of likelihood:")
    print("  1. SDA and SCL are swapped  (this is usually it)")
    print("  2. VCC is on 5V instead of 3V3, or not connected")
    print("  3. a jumper isn't seated -- wiggle each one")
    raise SystemExit

from ssd1306 import SSD1306_I2C

oled = SSD1306_I2C(128, 64, i2c, addr=found[0])

# border + crosshair: shows you every edge pixel is reachable
oled.fill(0)
oled.rect(0, 0, 128, 64, 1)
oled.hline(0, 32, 128, 1)
oled.vline(64, 0, 64, 1)
oled.text("wish tin", 32, 12, 1)
oled.text("screen ok", 28, 40, 1)
oled.show()
print("drew a test pattern -- you should see a border, a cross, and two words")

time.sleep(2)
for c in range(255, -1, -5):     # prove the hardware contrast fade works
    oled.contrast(c)
    time.sleep_ms(12)
for c in range(0, 256, 5):
    oled.contrast(c)
    time.sleep_ms(12)
print("fade ok -- this is what Act I and Act III use")
