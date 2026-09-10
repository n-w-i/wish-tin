# wish tin

A tin with a candle in it and a small screen that keeps you company either side
of the wish. It shows a quote, then a flame you blow out, then a closing line.
It never shows the wish itself.

## Board: XIAO ESP32S3

Use the **Seeed XIAO ESP32S3**, not the Pico 2 W. It is 21x17.5mm against the
Pico's 51x21mm, which matters once a tea light is sharing the tin; the headers
are already soldered; it is USB-C, so it takes a power bank directly; and it has
WiFi *and* BLE, which is what the "log the wish to my phone" idea will need
later. The XIAO RP2040 is the same size and equally fine if you want to keep the
radio out of it -- swap the commented pin block in `main.py`.

Firmware: MicroPython **ESP32_GENERIC_S3**.
https://micropython.org/download/ESP32_GENERIC_S3/

## Wiring

No resistors. The buttons use the chip's internal pull-ups, so each one is just
a switch shorting a pin to ground.

| From | To | XIAO ESP32S3 pin |
|---|---|---|
| OLED VCC | 3V3 | 3V3 |
| OLED GND | GND | GND |
| OLED SDA | D4 | GPIO5 |
| OLED SCL | D5 | GPIO6 |
| Button A "begin" | D1 <-> GND | GPIO2 |
| Button B "blown out" | D2 <-> GND | GPIO3 |

Copy `main.py`, `scenes.py`, `quotes.py`, `ssd1306.py` to the board
(`mpremote cp *.py :`) and reset. On boot it prints the I2C addresses it found;
the OLED is almost always `0x3c`. If that list is empty, SDA and SCL are
swapped -- that is the failure nine times out of ten.

## Do you need a breadboard?

**Not for the tin.** Breadboard connections work loose in anything that gets
carried or knocked, and it would eat the space the candle needs. Solder short
silicone-insulated wires directly, and give the buttons a scrap of protoboard.

**Yes for the bench, sort of.** A 170-point mini (47x35mm, ~£2) is genuinely
nice for trying button placement before committing. But don't wait on the post:
the XIAO and the OLED both have headers, so four female-to-female jumpers get
you a working screen tonight, and you can hold a button's legs against D1 and
GND to test it.

## Fire

You already made the right call on the LiPo. Three more that are less obvious:

- **Hot glue softens at 60-70°C.** A tea light in a closed tin passes that. Glue
  things into the *lid*, never near the flame, and never rely on glue alone to
  hold the screen.
- **The OLED module is rated to about 70°C too.** Put the candle at one end and
  the electronics at the other, or mount the screen in the lid facing down at
  you. Short ceremonies, not hour-long burns.
- **Don't close the lid on a lit candle.** Metal, no oxygen, and hot glue --
  pick any two.

Use silicone-insulated wire if you have it; PVC insulation goes tacky and sags
at temperatures the tin will easily reach.

## Power banks

Most power banks cut out when they see less than ~50-100mA. The XIAO plus the
OLED sits right around that line, so it may switch itself off partway through a
wish. If that happens: use a bank with a "low current" or "trickle" mode, or a
plain USB wall adapter. Worth testing before the evening you actually want it.

## Later

- **A 5mm LED can read light.** Reverse-bias it and time how long it takes to
  discharge into an ADC pin: clear or red ones work best. That replaces Button B
  and the tin senses the candle going out by itself, with a part you already
  own. This is the upgrade that makes the whole thing feel like magic.
- **A servo** could lift a small paper flag, or nudge the lid, at the end.
- **The phone log.** The ESP32S3 can pull the real date over NTP and post
  "a wish was made, 10 Sept 2026" somewhere you keep things. BLE is the better
  route than WiFi -- no hotspot, no credentials in the tin. Worth doing after
  the hardware feels right, not before.

## Quickstart

Install the tools with `uv tool install mpremote && uv tool install esptool`,
then fetch the firmware (not committed -- it's a 1.7MB binary):

```
mkdir -p firmware && curl -L -o firmware/ESP32_GENERIC_S3-v1.29.0.bin \
  https://micropython.org/resources/firmware/ESP32_GENERIC_S3-20260824-v1.29.0.bin
```
 Do these in order and stop at the first one that misbehaves.

```
# 1. flash MicroPython -- once only.
#    Bootloader mode first: hold BOOT, tap RESET, release BOOT.
./flash.sh

# 2. board alive? no wiring needed.
mpremote run 00_blink.py

# 3. screen. wire 4 jumpers first: VCC->3V3 GND->GND SDA->D4 SCL->D5
mpremote cp ssd1306.py : && mpremote run 01_screen_test.py

# 4. buttons. D1->GND and D2->GND
mpremote run 02_button_test.py

# 5. the whole ceremony
./deploy.sh
```

`mpremote run` executes a file without installing it, so steps 2-4 leave the
board clean. Only `deploy.sh` copies anything permanently.

## Credits

`ssd1306.py` is the standard MicroPython SSD1306 driver (MIT), from
micropython-lib via https://github.com/stlehmann/micropython-ssd1306 --
vendored here so the board only ever needs four files copied to it.

Everything else is written for this tin.
