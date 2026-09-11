# Step 6: is the button wired correctly?
#   One leg -> D1 (GPIO2),  diagonal leg -> D0 (GPIO1)
# Nothing goes to the real GND pin -- that belongs to the OLED. D0 is driven
# LOW in software and acts as the button's ground.
import time
from machine import Pin

Pin(1, Pin.OUT).value(0)          # local ground
btn = Pin(2, Pin.IN, Pin.PULL_UP)

print("press the button -- ctrl-C to stop")
print("reads 1 untouched, 0 when held")
print("if it reads 0 constantly, both wires are on the same side of the switch")
last = None
n = 0
while True:
    v = btn.value()
    if v != last:
        if v == 0:
            n += 1
            print("  PRESS %d" % n)
        last = v
    time.sleep_ms(20)
