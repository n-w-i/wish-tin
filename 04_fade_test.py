# Watch the dissolve. Same code Acts I and III use.
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

for text in ("A candle is just\na small argument\nwith the dark.",
             "Filed with the\nothers.\n\nThey are all\nstill pending."):
    scenes.block(oled, text, show=False)
    scenes.fade_in(oled)
    time.sleep(3)
    scenes.fade_out(oled)
    time.sleep_ms(600)
print("two dissolves done")
