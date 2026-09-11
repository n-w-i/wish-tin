# main.py -- the wish tin.
#
# Board:   Seeed XIAO ESP32S3   (swap the pin block below for XIAO RP2040)
# Screen:  0.96" SSD1306 128x64 OLED, I2C, stood upright at the back of the tin
# Input:   one 12mm tactile button -- press to begin, press again once the
#          real candle is out. The sequence is strictly ordered, so a single
#          button reading as "advance" beats two you'd have to tell apart in
#          the dark.
# Power:   USB-C from a power bank. No battery in the tin: there is a flame.
import time
from machine import Pin, I2C, SoftI2C

import quotes
import scenes
from ssd1306 import SSD1306_I2C

# ---- pins ----------------------------------------------------------------
# XIAO ESP32S3:  D4 = GPIO5 (SDA), D5 = GPIO6 (SCL)
PIN_SDA, PIN_SCL = 5, 6

# Each button gets its own pair of adjacent pins: one input with a pull-up,
# and a neighbour driven LOW as a local ground. The board only breaks out one
# real GND and the OLED has it. A press draws ~70uA through the 45k pull-up,
# against a 40mA sink limit -- nothing to worry about.
# GPIO3 is avoided deliberately: it's an ESP32-S3 strapping pin.
PIN_BUTTON, PIN_BUTTON_GND = 2, 1  # D1 + D0   (left side, 2nd and 1st down)
# D8/D9 left free for the LED light sensor that will one day replace the
# second press entirely.

WISH_TIMEOUT_MS = 150000        # if you never press "blown", end kindly anyway
QUOTE_HOLD_MS = 9000            # Act I, how long the opening line stays up
CLOSING_HOLD_MS = 8000          # Act III, same for the closing line
MIN_WISH_MS = 2500              # you cannot blow out a candle you just lit
LIGHT_TIMEOUT_MS = 180000       # if the candle never gets lit, quietly give up


class Button:
    """Active-low, internal pull-up, 40ms debounce, rising-edge trigger.
    gnd_gpio is a neighbouring pin held LOW to act as this button's ground."""

    def __init__(self, gpio, gnd_gpio):
        self.gnd = Pin(gnd_gpio, Pin.OUT)
        self.gnd.value(0)
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
    """Idle: the same sky as Act IV, thinned almost to nothing. The tin goes
    quiet by emptying out rather than by switching to something else."""
    sky = scenes.Sky()
    oled.contrast(255)
    t = 0
    while True:
        if btn.pressed():
            return
        if t % 5 == 0:
            sky.step(oled)
        time.sleep_ms(25)
        t += 1


def ceremony(oled, btn):
    sparks = scenes.Sparks()

    # Act I -- the quote.
    scenes.block(oled, quotes.opening(), show=False)
    scenes.fade_in(oled)
    time.sleep_ms(QUOTE_HOLD_MS)
    scenes.fade_out(oled)

    # Act II -- light it, wish, blow it out.
    scenes.block(oled, "light it", show=False)
    scenes.fade_in(oled)
    btn.pressed()                      # swallow the edge that began Act I
    waited = time.ticks_ms()
    while not btn.pressed():           # hold here until the candle is lit
        if time.ticks_diff(time.ticks_ms(), waited) > LIGHT_TIMEOUT_MS:
            scenes.fade_out(oled)      # never mind -- back to idle
            return
        time.sleep_ms(20)
    scenes.fade_out(oled)

    t = 0
    start = time.ticks_ms()
    btn.pressed()                      # swallow the "it is lit" press
    while True:
        held = time.ticks_diff(time.ticks_ms(), start)
        if held > MIN_WISH_MS and btn.pressed():
            break
        if held > WISH_TIMEOUT_MS:
            break
        scenes.wishing(oled, sparks, t)
        time.sleep_ms(55)
        t += 1

    scenes.blow_out(oled, sparks)
    time.sleep_ms(500)

    # Act III -- the receipt.
    scenes.block(oled, quotes.closing(), show=False)
    scenes.fade_in(oled)
    time.sleep_ms(CLOSING_HOLD_MS)
    scenes.fade_out(oled)

    # Act IV -- and there they are.
    scenes.starfield(oled)


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
    btn = Button(PIN_BUTTON, PIN_BUTTON_GND)

    while True:
        wait_for(btn, oled)
        ceremony(oled, btn)


main()
