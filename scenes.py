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


def block(oled, text, hold=0, clear=True, show=True):
    """Draw a centred block of text. show=False leaves it in the buffer
    unsent, which is how fade_in gets something to dissolve up to."""
    lines = wrap(text)[:ROWS]
    if clear:
        oled.fill(0)
    y0 = (H - len(lines) * 8) // 2
    for i, ln in enumerate(lines):
        x = (W - len(ln) * 8) // 2
        oled.text(ln, max(x, 0), y0 + i * 8, 1)
    if show:
        oled.show()
    if hold:
        time.sleep_ms(hold)


# Ordered 4x4 Bayer dither. On a 1-bit panel this reads as a dissolve, and it
# has far more range than the contrast register -- these modules barely dim,
# so a brightness ramp is close to invisible. Dispersing suits the tin better
# than dimming anyway.
_BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))
_MASKS = tuple(
    bytes(sum(1 << i for i in range(8) if _BAYER[i % 4][x] < L) for x in range(4))
    for L in range(17)
)


def _dissolve(oled, levels, delay):
    """Mask the live buffer against a dither at each level. Width is 128, a
    multiple of 4, so the byte's column is just i & 3."""
    orig = bytearray(oled.buffer)
    buf = oled.buffer
    n = len(buf)
    for L in levels:
        m = _MASKS[L]
        for i in range(n):
            buf[i] = orig[i] & m[i & 3]
        oled.show()
        time.sleep_ms(delay)
    return orig


def fade_in(oled, delay=38):
    """Dissolve up to whatever block() left in the buffer."""
    orig = _dissolve(oled, range(17), delay)
    buf = oled.buffer
    for i in range(len(buf)):
        buf[i] = orig[i]
    oled.show()


def fade_out(oled, delay=38):
    _dissolve(oled, range(16, -1, -1), delay)
    oled.fill(0)
    oled.show()


def _flame(oled, cx, base, t):
    """A teardrop that never sits still. Height and lean wander per frame."""
    h = 14 + (t % 3) + random.getrandbits(2)
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

    def step(self, oled, drift=1, respawn=True):
        """respawn=False lets the embers die out instead of feeding back in
        from the bottom -- during the blow-out that would read as the fire
        still burning."""
        for s in self.p:
            s[1] += s[2]
            if drift:
                s[0] += random.getrandbits(1) - random.getrandbits(1)
            s[3] -= 1
            if s[3] <= 0 or s[1] < 0:
                if not respawn:
                    continue
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
    for t in range(44):
        oled.fill(0)
        sparks.step(oled, drift=1, respawn=False)
        # smoke: a sine-ish ribbon rising from the dead wick. head is the
        # top of the column, and only the last TAIL rows are drawn, so the
        # bottom thins out behind it as it climbs.
        head = (t * 3) // 2
        for i in range(min(head, 44)):
            y = 52 - i
            x = W // 2 + int(3 * (1 if (i // 5) % 2 else -1) * (i / 44.0))
            if head - i < 20:
                oled.pixel(x, y, 1)
        oled.show()
        time.sleep_ms(45)

class Meteor:
    """A streak crossing the sky. Position is tracked in half-pixels so it
    can travel slower than one pixel a frame -- integers have no gear below
    that, and at full speed it crosses before you've looked up."""

    def __init__(self):
        self.life = 0

    def start(self):
        self.x = random.getrandbits(8)         # half-pixels: 0..255
        self.y = random.getrandbits(5)         # starts high
        self.vx = 2 + random.getrandbits(1)    # 1.0 or 1.5 px per frame
        if random.getrandbits(1):
            self.vx = -self.vx
        self.vy = 1                            # 0.5 px per frame
        self.life = 40 + random.getrandbits(4)

    def step(self, oled):
        if self.life <= 0:
            return
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if not (0 <= (self.x >> 1) < W) or (self.y >> 1) >= H:
            self.life = 0
            return
        # head, then a tail tracing where it has just been
        for i in range(6):
            if i > 2 and (i + self.life) & 1:
                continue
            x = (self.x - self.vx * i) >> 1
            y = (self.y - self.vy * i) >> 1
            if 0 <= x < W and 0 <= y < H:
                oled.pixel(x, y, 1)
                if i == 0 and y > 0:
                    oled.pixel(x, y - 1, 1)    # head reads brighter


class Sky:
    """The idle screen: a sparse sky that slowly rearranges itself. Each star
    has a lifetime and moves elsewhere when it expires, so nothing sits lit in
    one place long enough to mark the panel. About ten pixels of 8192."""

    def __init__(self, n=10):
        self.p = [self._new() for _ in range(n)]
        self.meteor = Meteor()

    def _new(self):
        return [random.getrandbits(7), random.getrandbits(6),
                20 + random.getrandbits(6)]

    def step(self, oled):
        oled.fill(0)
        for s in self.p:
            s[2] -= 1
            if s[2] <= 0:
                s[:] = self._new()
            oled.pixel(s[0], s[1], 1)
        if self.meteor.life <= 0 and random.getrandbits(7) == 0:
            self.meteor.start()
        self.meteor.step(oled)
        oled.show()


def starfield(oled, n=70, rise=52, hold=36, setting=64):
    """Act IV. A sea of stars arrives, breathes, and goes out. Ends on an
    empty screen, which the idle Sky then quietly repopulates."""
    xs = bytearray(n)
    ys = bytearray(n)
    ph = bytearray(n)
    for i in range(n):
        xs[i] = random.getrandbits(7)
        ys[i] = random.getrandbits(6)
        ph[i] = random.getrandbits(4)

    met = Meteor()
    when = rise + (random.getrandbits(6) % hold)   # one, but never on cue

    total = rise + hold + setting
    for t in range(total):
        if t == when:
            met.start()
        if t < rise:
            k = (n * (t + 1)) // rise
        elif t < rise + hold:
            k = n
        else:
            k = (n * (total - t)) // setting
        oled.fill(0)
        for i in range(k):
            # a quarter of them breathe, so the field is never quite still
            if ph[i] < 4 and ((t >> 3) + ph[i]) & 3 == 0:
                continue
            oled.pixel(xs[i], ys[i], 1)
        met.step(oled)
        oled.show()
        time.sleep_ms(45)
    oled.fill(0)
    oled.show()
