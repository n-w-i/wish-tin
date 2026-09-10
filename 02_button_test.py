# Step 2: are the buttons wired correctly?
#   Button A: one leg -> D1 (GPIO2),  other leg -> GND
#   Button B: one leg -> D2 (GPIO3),  other leg -> GND
# No resistors. 6mm tactile buttons have FOUR legs: the pairs across the
# short axis are already connected inside, so use one leg from each side.
import time
from machine import Pin

a = Pin(2, Pin.IN, Pin.PULL_UP)
b = Pin(3, Pin.IN, Pin.PULL_UP)

print("press each button -- ctrl-C to stop")
print("(both should read 1 when untouched, 0 when held)")
last = None
while True:
    now = (a.value(), b.value())
    if now != last:
        print("  A=%d  B=%d  %s" % (now[0], now[1],
              "<- A pressed" if now[0] == 0 else "<- B pressed" if now[1] == 0 else ""))
        last = now
    time.sleep_ms(30)
