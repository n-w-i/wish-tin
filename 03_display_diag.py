# Does this panel actually obey contrast, invert and power commands?
# Uses a FULL WHITE screen -- contrast changes drive current, so it is only
# obvious when most pixels are lit.
import time
from machine import Pin, I2C, SoftI2C
from ssd1306 import SSD1306_I2C

try:
    i2c = I2C(0, sda=Pin(5), scl=Pin(6), freq=400000)
except Exception:
    i2c = SoftI2C(sda=Pin(5), scl=Pin(6), freq=400000)

oled = SSD1306_I2C(128, 64, i2c)


def white(label):
    oled.fill(1)
    oled.fill_rect(0, 26, 128, 12, 0)
    x = (128 - len(label) * 8) // 2
    oled.text(label, max(x, 0), 28, 1)
    oled.show()


print("1/5 FULL BRIGHT  (contrast 255)")
white("BRIGHT")
oled.contrast(255)
time.sleep(2.5)

print("2/5 FULL DIM     (contrast 1)  <- should be clearly dimmer")
white("DIM")
oled.contrast(1)
time.sleep(2.5)

print("3/5 BRIGHT again (contrast 255)")
white("BRIGHT")
oled.contrast(255)
time.sleep(2.5)

print("4/5 INVERTED     (black on white -> white on black)")
oled.invert(1)
time.sleep(2.5)
oled.invert(0)

print("5/5 PANEL OFF    (2s of nothing), then edge test")
oled.poweroff()
time.sleep(2)
oled.poweron()

# SH1106 panels are offset 2px and clip the left/right edge of an SSD1306 draw.
oled.fill(0)
oled.rect(0, 0, 128, 64, 1)
oled.vline(2, 0, 64, 1)
oled.vline(125, 0, 64, 1)
oled.text("EDGES", 44, 28, 1)
oled.show()
print()
print("Edge test on screen now: an outer border plus two inner vertical lines.")
print("All four border edges visible = SSD1306. Left/right missing = SH1106.")
