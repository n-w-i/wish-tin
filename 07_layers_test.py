# Exercises every new scene without needing a button press. Run, don't install.
import time
from machine import Pin, I2C, SoftI2C
from ssd1306 import SSD1306_I2C
import scenes
import quotes

try:
    i2c = I2C(0, sda=Pin(5), scl=Pin(6), freq=400000)
except Exception:
    i2c = SoftI2C(sda=Pin(5), scl=Pin(6), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)
oled.contrast(255)

print("1/5 opener, word by word")
scenes.reveal(oled, quotes.opening())
time.sleep_ms(3500)
scenes.fade_out(oled)

print("2/5 light it, then the unlit candle")
words = scenes.reveal(oled, "light it")
time.sleep_ms(250)
cand = scenes.layer(scenes.candle)
scenes.layer_in(oled, words, cand)
time.sleep_ms(2000)

print("3/5 words go, candle stays, prompt arrives, wick catches")
scenes.layer_out(oled, cand, words)
prompt = scenes.layer(scenes.caption, "make a wish")
scenes.layer_in(oled, cand, prompt)

sparks = scenes.Sparks()
for t in range(90):
    scenes.wishing(oled, sparks, t)
    time.sleep_ms(55)

print("4/5 prompt goes, candle blown out")
scenes.layer_out(oled, cand, prompt)
scenes.blow_out(oled, sparks)
oled.fill(0)
scenes.candle(oled)
oled.show()
time.sleep_ms(700)
scenes.fade_out(oled)

print("5/5 done -- no crash")
