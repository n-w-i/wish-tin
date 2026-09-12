# scenes.py -- drawing and animation for a 128x64 mono OLED.
# The built-in font is 8x8, so: 16 columns, 8 rows. Everything is built
# around that grid.
import framebuf
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


# A layer is a full-screen buffer holding one element on its own, so it can
# dissolve in or out without disturbing anything else on screen. This is what
# lets the candle stay lit while the words around it come and go.
_TMP = bytearray(W * H // 8)
_TMPFB = framebuf.FrameBuffer(_TMP, W, H, framebuf.MONO_VLSB)

_IN = (3, 7, 11, 14, 16)
_OUT = (14, 11, 7, 3, 0)


def layer(draw, *args):
    """Render a drawing function into a buffer of its own."""
    _TMPFB.fill(0)
    draw(_TMPFB, *args)
    return bytearray(_TMP)


def _composite(oled, base, over, levels, delay):
    buf = oled.buffer
    n = len(buf)
    for L in levels:
        m = _MASKS[L]
        for i in range(n):
            buf[i] = base[i] | (over[i] & m[i & 3])
        oled.show()
        time.sleep_ms(delay)


def layer_in(oled, base, over, delay=18):
    """Dissolve `over` in on top of `base`."""
    _composite(oled, base, over, _IN, delay)


def layer_out(oled, base, over, delay=18):
    """Dissolve `over` away, leaving `base` behind."""
    _composite(oled, base, over, _OUT, delay)


def _word(fb, w, x, y):
    fb.text(w, x, y, 1)


def reveal(oled, text, delay=18, gap=40):
    """Words arrive one at a time, each dissolving in rather than snapping on,
    and each landing in its final position so nothing reflows.
    Returns the finished image as a layer, for dissolving out later."""
    lines = wrap(text)[:ROWS]
    y0 = (H - len(lines) * 8) // 2
    solid = bytearray(len(oled.buffer))
    oled.fill(0)
    oled.show()
    for li, ln in enumerate(lines):
        x0 = max((W - len(ln) * 8) // 2, 0)
        col = 0
        for w in ln.split(" "):
            if w:
                word = layer(_word, w, x0 + col * 8, y0 + li * 8)
                _composite(oled, solid, word, _IN, delay)
                for i in range(len(solid)):
                    solid[i] |= word[i]
                time.sleep_ms(gap)
            col += len(w) + 1
    return solid


def caption(fb, s, y=8):
    fb.text(s, max((W - len(s) * 8) // 2, 0), y, 1)


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


def candle(oled, cx=W // 2, base=47, lit=False, t=0, grow=16):
    """The candle itself, at the same coordinates lit or unlit, so the one
    on the light-it screen is the one that catches."""
    top = base + 5
    oled.fill_rect(cx - 3, top, 7, H - top, 1)   # body, off the bottom edge
    oled.vline(cx, base + 1, 4, 1)               # wick
    if lit:
        _flame(oled, cx, base, t, grow)


def _flame(oled, cx, base, t, grow=16):
    """A teardrop that never sits still. Height and lean wander per frame.
    grow < 16 scales it down, so the flame climbs as the wick catches."""
    h = 14 + (t % 3) + random.getrandbits(2)
    if grow < 16:
        h = (h * grow) // 16
        if h < 2:
            h = 2
    lean = random.getrandbits(1) - random.getrandbits(1)
    for i in range(h):
        y = base - i
        f = i / h
        half = int((1 - abs(f - 0.35) * 2.1) * 4)
        if half < 0:
            half = 0
        x = cx + int(lean * f * 2)
        oled.hline(x - half, y, half * 2 + 1, 1)



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
    """Act II: the flame is lit and burning. One frame. The prompt stays up
    for the whole wish; the flame climbs over the first second as it catches."""
    oled.fill(0)
    sparks.step(oled)
    candle(oled, lit=True, t=t, grow=min(16, 2 + t))
    caption(oled, prompt)
    oled.show()


def blow_out(oled, sparks):
    """Act II ends: flame gone, embers scatter, smoke climbs and thins."""
    sparks.burst(W // 2, 46)
    for t in range(44):
        oled.fill(0)
        sparks.step(oled, drift=1, respawn=False)
        candle(oled)                       # still there, just out
        # smoke: a sine-ish ribbon rising from the dead wick. head is the
        # top of the column, and only the last TAIL rows are drawn, so the
        # bottom thins out behind it as it climbs.
        head = (t * 3) // 2
        for i in range(min(head, 44)):
            y = 47 - i
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
