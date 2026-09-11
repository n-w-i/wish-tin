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

CLOSING = (
    "Out there\nwith the stars.",
    "Sent.\n\nGo and be\nunreasonable\nabout it.",
    "The tin will\nkeep this one.\n\nYou may forget\nit now.",
    "Filed with the\nothers.\n\nThey are all\nstill pending.",
    "Noted, and\nnot repeated\nto anyone.",
    "Well asked.\n\nNow put it down\nand go to bed.",
)


def opening():
    return random.choice(OPENING)


def closing():
    return random.choice(CLOSING)
