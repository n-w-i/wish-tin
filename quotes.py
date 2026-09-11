# quotes.py -- the words either side of the wish.
#
# Both lines are fixed. A line that varies is a random draw; a line that
# repeats is a ritual. Retired alternatives are kept below rather than
# deleted, so any of them can be brought back with one edit.
#
# The screen is a 16 x 8 grid: the built-in font is 8x8 on a 128x64 panel.
# Keep every line under 16 characters.

OPENING = 'You are allowed\nto ask for this.'

CLOSING = "It's out there\nwith the stars."


_RETIRED_OPENINGS = (
    'Light it slowly.\nThe good wishes\nare not in a\nhurry.',
    'A candle is just\na small argument\nwith the dark.',
    'Whatever you are\nabout to ask for,\nask for the\nbigger version.',
    'You are allowed\nto want it\nplainly.',
    'Somewhere this\nwish is already\nold news.',
    'Wish for the\nthing, not for\npermission to\nwant the thing.',
    'The smoke knows\nthe way. It has\ndone this\nbefore.',
)

_RETIRED_CLOSINGS = (
    'Sent.\\n\\nGo and be\\nunreasonable\\nabout it.',
)


def opening():
    return OPENING


def closing():
    return CLOSING
