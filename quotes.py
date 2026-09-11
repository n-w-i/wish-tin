# quotes.py -- Act I. Shown before the wish, one at random.
# Keep lines under ~16 characters per word-group; the 8x8 font gives 16 per row.
import random

OPENING = (
    "Light it slowly.\nThe good wishes\nare not in a\nhurry.",
    "A candle is just\na small argument\nwith the dark.",
    "Whatever you are\nabout to ask for,\nask for the\nbigger version.",
    "You are allowed\nto want it\nplainly.",
    "Somewhere this\nwish is already\nold news.",
    "Wish for the\nthing, not for\npermission to\nwant the thing.",
    "The smoke knows\nthe way. It has\ndone this\nbefore.",
)

# The closing line never changes. An ending that varies is a random draw;
# an ending that is always the same is a ritual.
CLOSING = "It's out there\nwith the stars."

# Retired closings, kept in case the dry register is ever wanted back.
_RETIRED = (
    "Sent.\\n\\nGo and be\\nunreasonable\\nabout it.",
)


def opening():
    return random.choice(OPENING)


def closing():
    return CLOSING
