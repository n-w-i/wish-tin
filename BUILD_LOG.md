# Wish tin — build log and decision record

Written 10 September 2026. Everything here is *why*, not just *what* — the
wiring is easy to rediscover, the reasoning isn't.

**Status: working end to end on hardware, 11 September 2026.** Flashed,
wired, soldered, and run through all three acts on the real panel.

---

## What we're building

A tin holding a lit tea light and a small OLED screen. You press a button and
it runs a three-act ceremony:

1. **Before** — a quote fades in and holds. One of seven, at random.
2. **Light it** — `light it` dissolves in and simply waits. Nothing moves until
   you press to say the real candle is burning, and the words dissolve away as
   you do. No instructions on screen; the tin trusts you to know.
3. **During** — `make a wish`, then a flickering flame with embers drifting up.
   You make your wish, blow the real candle out, and press again. The on-screen
   flame dies, embers scatter, smoke climbs and thins.
4. **After** — `It's out there with the stars.` Always the same line: an ending
   that varies is a random draw, an ending that repeats is a ritual.

Three presses total, all on the one button: **begin**, **lit**, **blown out**.

**The wish itself is never shown.** That was the requirement from the start, and
it's why the earlier wish-*generator* code was deleted rather than kept around.
The tin is company either side of the wish, not a participant in it.

---

## How we got here

### It started as "what model should I run?"

The original question was which model to run locally. The answer that came back
from the HuggingFace leaderboards was genuinely interesting and worth keeping:

**`Qwen/Qwen3-4B-Instruct-2507` scores 69.6 on MMLU-Pro** — rank 45 of 140,
above Qwen2.5-32B (69.2), DeepSeek-V3 (64.4) and Llama-3.1-405B (61.6). A 4B
model beating a 405B one. The next best model in its size class is 17 points
behind, so it isn't close.

### Then the hardware arrived and killed it

A Pico 2 W has **520KB of SRAM**. That 4B model needs roughly **1.8GB** at Q4.
That's about **3,500× short** — no quantization or pruning closes it. So the tin
does not think, and never did. Everything after this point is built around that.

This is also why the project stopped needing WiFi. An early version served a web
page to a phone because the phone had to be the display. Once a real 0.96" OLED
was on the parts list, the phone became unnecessary and the whole network layer
was deleted. Simpler, and it works with no signal.

---

## Why each part

| Part | Why this one |
|---|---|
| **Seeed XIAO ESP32S3** | 21×17.5mm vs the Pico 2 W's 51×21mm — matters once a tea light shares the tin. Headers pre-soldered, USB-C (power bank plugs straight in), and BLE for the deferred phone-logging idea. |
| **XIAO RP2040** | Same size, no radio. Fine alternative — swap the commented pin block in `main.py`. Rejected only because BLE is wanted later. |
| **Pico 2 W** | Rejected: 2.4× the footprint for no benefit here. |
| **0.96" SSD1306 OLED** | Tiny, I2C (2 wires), and it has a *hardware contrast register* — so the fades are real dimming, not a dithering trick. |
| **6mm tactile buttons** | Two: "begin" and "blown out". No resistors needed — the chip's internal pull-ups mean each button is just a switch to ground. |
| **USB power bank** | See below. |
| **500mAh LiPo** | **Deliberately unused.** There is an open flame in this enclosure. |

### The battery decision

Nina's call, and the right one: no lithium cell inside a tin with a lit candle.
The power bank sits outside on a USB-C cable, which puts distance between the
cell and the flame. This isn't caution theatre — it's the one genuinely
unsafe version of this project, and it's now designed out.

### The heat constraints that follow

- **Hot glue softens at 60–70°C.** A tea light in a closed metal tin passes
  that. Glue into the *lid*, never near the flame, and never rely on glue alone
  to hold the screen.
- **The OLED module is rated to about 70°C** — the same range. Candle at one
  end, electronics at the other, or screen mounted in the lid facing down.
- **Never close the lid on a lit candle.** Metal, no oxygen, hot glue.
- **Silicone-insulated wire** if available. PVC goes tacky and sags at
  temperatures this tin will reach easily.

### The power bank gotcha

Most power banks cut out below **~50–100mA**. The XIAO plus the OLED sits right
on that line, so the bank may switch itself off partway through a wish. If that
happens: use a bank with a "low current" or "trickle" mode, or a wall adapter.
**Test this before the evening you actually want it working.**

---

## Do you need a breadboard?

**Not for the tin.** Breadboard connections work loose in anything carried or
knocked, and it would eat the space the candle needs. Solder short wires; give
the buttons a scrap of protoboard.

**Useful on the bench, but not blocking.** A 170-point mini (47×35mm, ~£2) is
nice for trying button placement. But the XIAO and the OLED both have headers,
so four female-to-female jumpers get a working screen with no soldering at all.

---

## Wiring

No resistors anywhere.

| From | To | XIAO ESP32S3 pin |
|---|---|---|
| OLED VCC | 3V3 | 3V3 |
| OLED GND | GND | GND |
| OLED SDA | D4 | GPIO5 |
| OLED SCL | D5 | GPIO6 |
| Button A "begin" | D1 ↔ GND | GPIO2 |
| Button B "blown out" | D2 ↔ GND | GPIO3 |

**6mm tactile buttons have four legs, and the pairs across the short axis are
already connected inside.** Take one leg from each side. Two legs from the same
side is a permanently-closed switch, and it's a confusing twenty minutes if you
don't know to look for it.

---

## Steps to follow

Tools are installed (`mpremote`, `esptool`, via `uv`). Do these in order and
stop at the first one that misbehaves.

```bash
cd ~/wish-tin

# 1. Flash MicroPython — once only.
#    Bootloader mode FIRST: hold BOOT, tap RESET, release BOOT.
#    (Both tiny buttons are beside the USB port.)
./flash.sh
#    Tap RESET when it finishes.

# 2. Is the board alive? No wiring needed at all.
mpremote run 00_blink.py
#    The small orange LED by the USB port blinks 10×.
#    If this works, board + cable + firmware are all good, and anything
#    that breaks later is wiring.

# 3. The screen. Wire the 4 jumpers first (VCC/GND/SDA/SCL above).
mpremote cp ssd1306.py : && mpremote run 01_screen_test.py
#    Expect: border, crosshair, "wish tin", then a slow fade out and back in.
#    That fade is the same hardware register Acts I and III use — seeing it
#    here means the nicest part already works.

# 4. The buttons. D1→GND and D2→GND.
mpremote run 02_button_test.py
#    Both read 1 untouched, 0 when held.

# 5. The whole ceremony.
./deploy.sh
```

`mpremote run` executes a file **without installing it**, so steps 2–4 leave the
board clean. Only `deploy.sh` copies anything permanently. This also means you
can edit `quotes.py` or the flame in `scenes.py` and re-run instantly.

### If the screen shows nothing

The I2C scan in `01_screen_test.py` prints what it found and ranks the likely
causes. In order:

1. **SDA and SCL are swapped.** This is it roughly nine times out of ten.
2. VCC is on 5V instead of 3V3, or not connected.
3. A jumper isn't seated — wiggle each one.

An empty scan list means the bus is wrong. `0x3c` is the address you want.

---

## The code

Four files go on the board. That's the whole runtime.

- **`main.py`** — state machine. Idle (a single breathing pixel, so the OLED
  isn't holding a bright static image for hours) → Act I → Act II → Act III.
  Debounced buttons, 40ms, rising edge.
- **`scenes.py`** — all the drawing. The built-in font is 8×8, so the screen is
  a **16 column × 8 row grid** and everything is built around that. The flame
  re-rolls its height and lean every frame; embers are a 14-particle system
  reused for the scatter when the candle goes out.
- **`quotes.py`** — the opening and closing lines. **This is the file to edit.**
  Every line is checked to wrap inside 16 characters.
- **`ssd1306.py`** — the standard MicroPython driver (MIT, from
  micropython-lib). Vendored so the board only ever needs four files.

Not on the board: the `0x_` test scripts, the shell helpers, this log.

---

## Repo

`github.com/n-w-i/wish-tin`, **private**, branch `main`.

Deliberately gitignored:
- `firmware/*.bin` — 1.7MB binary, fetched not authored. README has the URL.
- `secrets.py` — doesn't exist yet, but will the moment the BLE work starts.
  Better to have the rule in place before there's anything in the file.

---

## Deferred, in order of how much they'd change the feel

1. **A 5mm LED can read light.** Reverse-bias one and time how long it takes to
   discharge into an ADC pin — clear or red ones work best. That replaces Button
   B entirely and the tin senses the candle going out *by itself*, using a part
   already in the drawer. This is the upgrade that makes it feel like magic.
2. **Tune the timings.** The flicker rate, the 6.5s quote hold, the fade speeds
   — all guessed blind. They want a real pair of eyes in a dark room.
3. **A servo** lifting a small paper flag at the end.
4. **The phone log** — "a wish was made, 10 Sept 2026", saved somewhere. The
   ESP32S3 can pull the real date over NTP. **BLE is the better route than
   WiFi**: no hotspot, no credentials living in the tin. Worth doing after the
   hardware feels right, not before.
