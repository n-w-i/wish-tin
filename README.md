# wish tin

A tin with a candle in it and a tiny screen that keeps me company either side of
the wish. It shows me something before, a flame while I'm wishing, and something
after — and it never, ever shows the wish itself.

It was a really easy project to do, but it was super whimsy. Here's the whole
thing start to finish, in the order I actually did it.

## 1. Choosing the right board

I went with the **XIAO ESP32S3** over something like a Raspberry Pi Pico because
I don't need it to have an operating system at all. It's just running one
programme in a loop. All I need it to do is work out when a button has been
pressed and show the right messages on the screen.

It was also really useful because **the headers were pre-soldered**, and I hate
soldering headers. It has USB-C built in too, so I can plug a cable straight in
to connect it to my phone. Down the line I'd quite like to make it so that it
records my wishes through my phone — I'm going to be doing a macro for that at
some point as well.

The XIAO RP2040 is the same size and equally fine if you want to keep the radio
out of it — swap the commented pin block in `main.py`.

## 2. The screen and the button

I went with an OLED screen, **0.96 inches, an SSD1306**. Super cheap, and it
makes things show up really nicely on the screen itself. It also has a hardware
contrast register, which is why the fades were meant to be real dimming rather
than a trick — see step 4 for how that went.

I also went with a **12mm tactile button**. I have some 6mm ones as well, but
they were just a little too small and fiddly for this project, because it also
involves real-life flames. I didn't want to make anything too fiddly to use.

That was all the actual equipment I needed, plus some **female-to-female jumper
wires** to connect things together.

## 3. Tools and firmware

I needed to install the tools, and then flash the firmware onto the board for
anything to run. I pulled the firmware from
[micropython.org](https://micropython.org/download/ESP32_GENERIC_S3/).

```bash
uv tool install mpremote
uv tool install esptool

mkdir -p firmware && curl -L -o firmware/ESP32_GENERIC_S3-v1.29.0.bin \
  https://micropython.org/resources/firmware/ESP32_GENERIC_S3-20260824-v1.29.0.bin
```

Then a classic bootloader on the ESP32-S3 — hold BOOT, tap RESET, release BOOT,
both tiny buttons are beside the USB port — and flash the firmware onto it.

```bash
./flash.sh          # tap RESET when it finishes
mpremote run 00_blink.py
```

I ran that quick blink test to make sure everything was awake and alive before I
went ahead and started securing hardware down into the actual physical thing.
Worth doing in that order: if the blink works, the board, the cable and the
firmware are all fine, so anything that breaks after this point is wiring.

## 4. Wiring up the OLED

I wired the OLED up to the ESP32-S3 using **four female-to-female jumper cables**
— power, ground, and the two data lines. No resistors anywhere.

| From | To | XIAO ESP32S3 pin |
|---|---|---|
| OLED VCC | 3V3 | 3V3 |
| OLED GND | GND | GND |
| OLED SDA | D4 | GPIO5 |
| OLED SCL | D5 | GPIO6 |

```bash
mpremote cp ssd1306.py : && mpremote run 01_screen_test.py
```

Then I tested the screen with a short script to make sure all the pixels were
working as they should, and that we could do different things like fading and
short animations.

**If the screen shows nothing**, the I2C scan in that script prints what it
found and ranks the likely causes. In order: SDA and SCL are swapped (this is it
roughly nine times out of ten), VCC is on 5V instead of 3V3 or not connected, or
a jumper isn't seated. An empty scan list means the bus is wrong. `0x3c` is the
address you want.

**On the fades.** I'd written the transitions using that contrast register, and
on the real panel a full 255-to-1 ramp was almost invisible — these modules
barely dim. The words dissolve through a 4x4 ordered dither instead, dropping
pixels on a pattern until there's nothing left. It goes all the way to black and
works on any panel.

## 5. Soldering the button

The button was a tactile button with four legs, so I had to get a little
creative. I took a female-to-female jumper cable and **cut it down the middle**,
stripping the ends back a little on each one. I tinned both the exposed wires and
two of the legs on the button first, then soldered them together.

I chose **two legs diagonally across from each other**. If you choose legs that
are laterally across from each other they basically serve the same purpose, so
you can't do that — they're already connected inside the switch. I had to choose
different legs. It's a confusing twenty minutes if you don't know to look for it.

Then I tested that the button was reading and that my soldering wasn't rubbish. I
put a little bit of **electrical tape** around where I joined the jumper cables
to the legs, for insulation and to give it a bit more stability.

```bash
mpremote run 02_button_test.py     # reads 1 untouched, 0 when held
```

**It's one button, not two.** I'd wired it for a begin button and a blown-out
button, then realised the sequence is strictly linear, so one button reading as
"advance" does the job. One less hole, one less pair of joints, and one thing to
find by feel in the dark.

| From | To | XIAO ESP32S3 pin |
|---|---|---|
| Button | D1 | GPIO2, input with internal pull-up |
| Button other leg | D0 | GPIO1, driven LOW as a local ground |

The button gets its own fake ground because the board only breaks out one real
GND and the OLED has it. A press draws ~70uA through the 45k pull-up against a
40mA sink limit, so there's nothing to worry about there. GPIO3 is avoided
deliberately — it's an ESP32-S3 strapping pin. D8/D9 are left free for the LED
light sensor that might one day replace the last press.

## 6. Deciding what appears on the screen

After that I got to work deciding what I wanted to appear on the screen, and
started choosing some fun quotes and animations to show while I was doing the
wish.

```bash
./deploy.sh        # copies the four runtime files and resets
```

I used `mpremote run` while I was working so I could keep iterating on my quotes
and things without needing to install anything onto the board each time. Only
`deploy.sh` copies anything permanently.

The way I thought this through was that I wanted it to relate to **the universe
and the stars**, because that's something I really enjoy and find a lot of
meaning in.

`quotes.py` is the file to edit. The built-in font is 8x8 on a 128x64 panel, so
the screen is a 16 column x 8 row grid — keep every line under 16 characters.
Retired alternatives are kept at the bottom of the file rather than deleted, so
any of them can come back with one edit.

## 7. What actually happens

**Idle.** Whenever the board has power, the screen shows this sea of stars just
idling. They twinkle a little, with an occasional shooting star.

**Press one.** When you're ready you press the button, and a nice introduction
quote fades in and then fades away. Another message comes up telling you to light
the candle, with an unlit candle on the screen as well. This stays for as long as
you need it to.

At this point you get your physical candle out, put it in the candle holder in
the tin, and light it.

**Press two.** Some phrasing comes up to tell you to make a wish. The digital
candle lights on the screen, with embers around it drifting away. You make your
wish in real life.

**Press three.** When it's done, you blow your candle out and press the button.
The digital candle also goes out, scatters, and smokes. It's very pretty. Another
message comes up to let you know your wish is now drifting in the universe, out
there with the stars — and it ends with this beautiful visual of a bunch of stars
and a shooting star, before returning to the idle screen.

**The wish itself is never shown.** That was the requirement from the start, and
it's why the earlier wish-*generator* code was deleted rather than kept around.
The tin is company either side of the wish, not a participant in it.

## 8. Testing before locking it down

I had to do some quick tests before actually locking everything into position. I
wanted to make sure it would **run properly from my phone**, because that makes
it super easy to just carry around with me.

**One thing to watch with power banks.** Most of them cut out when they see less
than ~50-100mA, and the XIAO plus the OLED sits right around that line, so the
bank may switch itself off partway through a wish. If that happens: use a bank
with a "low current" or "trickle" mode, or a plain USB wall adapter. Worth
testing before the evening you actually want it working.

## 9. Getting it into the tin

Then I got to work positioning the three components and a bunch of cables. I
ended up using the **deeper side of the tin** — technically the side where you're
supposed to keep your items — but it worked really well in terms of height for
mounting everything I needed to mount.

I used **Velcro** for a lot of it. The XIAO ESP32S3 is mounted to the side of the
tin with Velcro, and so is the screen, and the cables are tucked out of the way
at the back. The button is mounted on a **circular piece of foam**, which gives a
bit of cushion when you press it so it isn't pressing directly onto a hard
surface. That protects the button as well. It just sort of wedges in.

Velcro also means I can always take these components out and use them for other
projects, or pull things out if anything needs updating. Super easy to do.

## 10. The cover

I created a **cardboard visual** for the top of the candle tin as well, to cover
up all of the jankiness behind it.

And that was it.

## Fire

There's an open flame in this thing, so a few of these aren't optional.

- **No battery in the tin.** I have a 500mAh LiPo and it is deliberately unused.
  No lithium cell inside an enclosure with a lit candle — the power bank sits
  outside on a USB-C cable, which puts distance between the cell and the flame.
- **Hot glue softens at 60-70°C**, and a tea light in a closed tin passes that.
  Glue things into the *lid*, never near the flame, and never rely on glue alone
  to hold the screen.
- **The OLED module is rated to about 70°C too.** Candle at one end and the
  electronics at the other, or the screen mounted in the lid facing down at you.
  Short ceremonies, not hour-long burns.
- **A taper rather than a tea light.** Smaller flame, much less heat, and it's
  tall enough that the flame sits *beside* the screen rather than underneath it,
  so most of the rising heat misses the electronics. That makes tipping the main
  risk instead of heat, so the candle gets anchored in a puddle of its own wax.
- **Don't close the lid on a lit candle.** Metal, no oxygen, and hot glue — pick
  any two.
- **Use silicone-insulated wire** if you have it. PVC insulation goes tacky and
  sags at temperatures this tin will easily reach.

## The code

Four files go on the board. That's the whole runtime.

- **`main.py`** — the state machine. Idle, then the three acts. Debounced
  buttons, 40ms, rising edge. It also never gives up: an I2C blip mid-draw raises
  `OSError`, and left uncaught that kills the program and leaves the last frame
  sitting on screen, which looks exactly like a freeze. It rebuilds the display
  and carries on instead, so a glitch becomes a blink rather than a dead tin.
- **`scenes.py`** — all the drawing. The flame re-rolls its height and lean every
  frame so it never repeats, and there are fourteen embers drifting up past it,
  reused for the scatter when the candle goes out.
- **`quotes.py`** — the words either side of the wish. This is the file to edit.
- **`ssd1306.py`** — the standard MicroPython driver (MIT, from micropython-lib
  via [stlehmann/micropython-ssd1306](https://github.com/stlehmann/micropython-ssd1306)),
  vendored so the board only ever needs four files.

Not on the board: the `0x_` test scripts, the shell helpers, and the logs.

## Later

- **A 5mm LED can read light.** Reverse-bias one and time how long it takes to
  discharge into an ADC pin — clear or red ones work best. That replaces the last
  press and the tin senses the candle going out by itself, using a part I already
  own. This is the upgrade that would make the whole thing feel like magic.
- **Tune the timings.** The flicker rate, the quote holds, the fade speeds — all
  guessed blind. They want a real pair of eyes in a dark room.
- **A servo** could lift a small paper flag, or nudge the lid, at the end.
- **The phone log.** Writing down that a wish was made, when, and where — never
  the wish. Spec is in [PHONE_LOG.md](./PHONE_LOG.md). BLE is the better route
  than WiFi: no hotspot, and no credentials living in the tin.
