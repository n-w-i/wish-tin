# Three candle shapes, each unlit then lit. Pick one.
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
CX = 64


def shape_1(fb):                      # tall slim outline
    fb.rect(CX - 4, 48, 9, 16, 1)
    fb.vline(CX, 44, 4, 1)


def shape_2(fb):                      # tall, with a melted rim overhanging
    fb.rect(CX - 4, 49, 9, 15, 1)
    fb.hline(CX - 6, 48, 13, 1)
    fb.hline(CX - 6, 49, 13, 1)
    fb.vline(CX, 44, 4, 1)


def shape_3(fb):                      # slim and solid
    fb.fill_rect(CX - 3, 50, 7, 14, 1)
    fb.vline(CX, 46, 4, 1)


SHAPES = ((shape_1, 43, "1"), (shape_2, 43, "2"), (shape_3, 45, "3"))

for draw, base, name in SHAPES:
    print("shape", name)
    oled.fill(0)
    draw(oled)
    scenes.caption(oled, "shape " + name, 4)
    oled.show()
    time.sleep_ms(2500)
    for t in range(55):               # and lit
        oled.fill(0)
        draw(oled)
        scenes._flame(oled, CX, base, t, min(16, 2 + t))
        scenes.caption(oled, "shape " + name, 4)
        oled.show()
        time.sleep_ms(55)
    oled.fill(0)
    oled.show()
    time.sleep_ms(400)
print("done")
