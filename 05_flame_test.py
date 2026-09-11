# Tuning loop: flame, then blow-out. Skips the quotes so you can iterate.
import time
from machine import Pin, I2C, SoftI2C
from ssd1306 import SSD1306_I2C
import scenes

try:
    i2c = I2C(0, sda=Pin(5), scl=Pin(6), freq=400000)
except Exception:
    i2c = SoftI2C(sda=Pin(5), scl=Pin(6), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)
oled.contrast(255)

for run in range(2):
    sparks = scenes.Sparks()
    for t in range(70):                  # ~4s of burning
        scenes.wishing(oled, sparks, t)
        time.sleep_ms(55)
    scenes.blow_out(oled, sparks)
    time.sleep(1)
oled.fill(0); oled.show()
print("two burns done")
