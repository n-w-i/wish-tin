# scenes.py -- drawing and animation for a 128x64 mono OLED.
# The built-in font is 8x8, so: 16 columns, 8 rows. Everything is built
# around that grid.
import random
import time

W = const(128)
H = const(64)
COLS = const(16)
ROWS = const(8)


def wrap(text, cols=COLS):
    """Split on explicit newlines first, then word-wrap what is left."""
    out = []
    for para in text.split("\n"):
        if not para:
            out.append("")
            continue
        line = ""
        for word in para.split(" "):
            if not line:
                line = word
            elif len(line) + 1 + len(word) <= cols:
                line += " " + word
            else:
                out.append(line)
                line = word
        out.append(line)
    return out


def block(oled, text, hold=0, clear=True):
    """Draw a centred block of text."""
    lines = wrap(text)[:ROWS]
    if clear:
        oled.fill(0)
    y0 = (H - len(lines) * 8) // 2
    for i, ln in enumerate(lines):
        x = (W - len(ln) * 8) // 2
        oled.text(ln, max(x, 0), y0 + i * 8, 1)
    oled.show()
    if hold:
        time.sleep_ms(hold)


def fade_in(oled, step=8, delay=18):
    for c in range(0, 256, step):
        oled.contrast(c)
        time.sleep_ms(delay)


def fade_out(oled, step=8, delay=18):
    for c in range(255, -1, -step):
        oled.contrast(max(c, 0))
        time.sleep_ms(delay)
    oled.fill(0)
    oled.show()
    oled.contrast(255)


def _flame(oled, cx, base, t):
    """A teardrop that never sits still. Height and lean wander per frame."""
    h = 11 + (t % 3) + random.getrandbits(2)
    lean = random.getrandbits(1) - random.getrandbits(1)
    for i in range(h):
        y = base - i
        f = i / h
        half = int((1 - abs(f - 0.35) * 2.1) * 4)
        if half < 0:
            half = 0
        x = cx + int(lean * f * 2)
        oled.hline(x - half, y, half * 2 + 1, 1)
    # wick
    oled.vline(cx, base + 1, 3, 1)


class Sparks:
    """Embers drifting up. Reused for the scatter when the flame goes out."""

    def __init__(self, n=14):
        self.p = [self._new(True) for _ in range(n)]

    def _new(self, seed=False):
        return [
            random.getrandbits(7),                       # x
            random.getrandbits(6) if seed else H - 1,    # y
            -(1 + random.getrandbits(1)),                # vy
            8 + random.getrandbits(4),                   # life
        ]

    def step(self, oled, drift=1):
        for s in self.p:
            s[1] += s[2]
            if drift:
                s[0] += random.getrandbits(1) - random.getrandbits(1)
            s[3] -= 1
            if s[3] <= 0 or s[1] < 0:
                s[:] = self._new()
            if 0 <= s[0] < W and 0 <= s[1] < H:
                oled.pixel(s[0], s[1], 1)

    def burst(self, cx, cy):
        for s in self.p:
            s[0] = cx + random.getrandbits(3) - 4
            s[1] = cy - random.getrandbits(2)
            s[2] = -(1 + random.getrandbits(2))
            s[3] = 14 + random.getrandbits(4)


def wishing(oled, sparks, t, prompt="make a wish"):
    """Act II: the flame is lit and burning. One frame."""
    oled.fill(0)
    if (t // 12) % 2 == 0:                # prompt breathes slowly
        x = (W - len(prompt) * 8) // 2
        oled.text(prompt, max(x, 0), 4, 1)
    sparks.step(oled)
    _flame(oled, W // 2, 54, t)
    oled.show()


def blow_out(oled, sparks):
    """Act II ends: flame gone, embers scatter, smoke climbs and thins."""
    sparks.burst(W // 2, 50)
    for t in range(26):
        oled.fill(0)
        sparks.step(oled, drift=1)
        # smoke: a sine-ish ribbon rising from the dead wick
        for i in range(min(t * 2, 44)):
            y = 52 - i
            x = W // 2 + int(3 * (1 if (i // 5) % 2 else -1) * (i / 44.0))
            if t * 2 - i < 18:
                oled.pixel(x, y, 1)
        oled.show()
        time.sleep_ms(45)
