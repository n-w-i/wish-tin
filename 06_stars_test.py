# Act IV and the idle sky, without the rest of the ceremony.
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

scenes.block(oled, "It's out there\nwith the stars.", show=False)
scenes.fade_in(oled)
time.sleep(3)
scenes.fade_out(oled)

scenes.starfield(oled)

print("now the idle sky for 15s")
sky = scenes.Sky()
for _ in range(120):
    sky.step(oled)
    time.sleep_ms(125)
oled.fill(0); oled.show()
print("done")
