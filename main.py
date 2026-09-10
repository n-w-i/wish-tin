# main.py -- the wish tin.
#
# Board:   Seeed XIAO ESP32S3   (swap the pin block below for XIAO RP2040)
# Screen:  0.96" SSD1306 128x64 OLED, I2C
# Input:   two 6mm tactile buttons to GND
# Power:   USB-C from a power bank. No battery in the tin: there is a flame.
import time
from machine import Pin, I2C, SoftI2C

import quotes
import scenes
from ssd1306 import SSD1306_I2C

# ---- pins ----------------------------------------------------------------
# XIAO ESP32S3:  D4 = GPIO5 (SDA), D5 = GPIO6 (SCL), D1 = GPIO2, D2 = GPIO3
PIN_SDA, PIN_SCL = 5, 6
PIN_BEGIN, PIN_BLOWN = 2, 3
# XIAO RP2040:   PIN_SDA, PIN_SCL = 6, 7 ; PIN_BEGIN, PIN_BLOWN = 27, 28

WISH_TIMEOUT_MS = 150000        # if you never press "blown", end kindly anyway


class Button:
    """Active-low, internal pull-up, 40ms debounce, rising-edge trigger."""

    def __init__(self, gpio):
        self.pin = Pin(gpio, Pin.IN, Pin.PULL_UP)
        self.last = 1
        self.t = 0

    def pressed(self):
        v = self.pin.value()
        now = time.ticks_ms()
        if v == 0 and self.last == 1 and time.ticks_diff(now, self.t) > 40:
            self.last = 0
            self.t = now
            return True
        if v == 1:
            self.last = 1
        return False


def wait_for(btn, oled):
    """Idle. A single pixel breathing near the bottom, so the OLED isn't
    holding a bright static image for hours."""
    t = 0
    oled.contrast(255)
    while True:
        if btn.pressed():
            return
        if t % 20 == 0:
            oled.fill(0)
            on = (t // 20) % 2 == 0
            if on:
                oled.text("o", 60, 52, 1)
            oled.show()
        time.sleep_ms(25)
        t += 1


def ceremony(oled, begin, blown):
    sparks = scenes.Sparks()

    # Act I -- the quote.
    oled.contrast(0)
    scenes.block(oled, quotes.opening())
    scenes.fade_in(oled)
    time.sleep_ms(6500)
    scenes.fade_out(oled)

    # Act II -- light it, wish, blow it out.
    scenes.block(oled, "light it", hold=1800)
    t = 0
    start = time.ticks_ms()
    while True:
        if blown.pressed():
            break
        if time.ticks_diff(time.ticks_ms(), start) > WISH_TIMEOUT_MS:
            break
        scenes.wishing(oled, sparks, t)
        time.sleep_ms(55)
        t += 1

    scenes.blow_out(oled, sparks)
    time.sleep_ms(500)

    # Act III -- the receipt.
    oled.contrast(0)
    scenes.block(oled, quotes.closing())
    scenes.fade_in(oled)
    time.sleep_ms(6000)
    scenes.fade_out(oled)


def main():
    try:
        i2c = I2C(0, sda=Pin(PIN_SDA), scl=Pin(PIN_SCL), freq=400000)
    except Exception:
        i2c = SoftI2C(sda=Pin(PIN_SDA), scl=Pin(PIN_SCL), freq=400000)

    found = i2c.scan()
    print("i2c devices:", [hex(a) for a in found])
    if not found:
        raise RuntimeError("no OLED on I2C -- check SDA/SCL and 3V3")

    oled = SSD1306_I2C(scenes.W, scenes.H, i2c, addr=found[0])
    begin = Button(PIN_BEGIN)
    blown = Button(PIN_BLOWN)

    while True:
        wait_for(begin, oled)
        ceremony(oled, begin, blown)


main()
