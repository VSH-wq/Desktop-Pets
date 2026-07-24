"""
messages.py

Pools of short strings shown in the pet's speech bubble for different
events and moods. Keeping these separate from pet_app.py makes it easy
to add more lines or localize later without touching any logic.
"""

import random

GREETING = ["Hi there!", "Hello!", "*waves*", "Oh, it's you!"]

HAPPY_CLICK = [
    "Yay!", "That tickles!", "Hehe, again!", "Best day ever!",
    "You're the best!", "More pets please!",
]

HOP = ["Wheee!", "Look at me go!", "Boing!", "Exploring time!"]

SLEEP = ["Zzz...", "So sleepy...", "Five more minutes..."]

WAKE = ["Morning!", "I'm awake!", "Ahh, refreshed."]

DRAG = ["Whoa!", "Where are we going?", "Wheee, flying!", "Careful now!"]

FEED = ["Yum yum!", "Thank you!", "So good!", "My favorite!"]

CHASE_START = ["Catch me!", "Tag, you're it!", "Can't catch me!"]
CHASE_END = ["Phew, tired now.", "You almost got me!", "That was fun!"]

IDLE_CHATTER_HAPPY = ["Life is good.", "What a nice day.", "Just vibing.", "La la la~"]
IDLE_CHATTER_NEUTRAL = ["...", "Hmm.", "*yawns*", "Bored..."]
IDLE_CHATTER_SAD = ["I miss you...", "Feeling a bit lonely.", "Pet me?", "*sighs*"]


def pick(pool):
    return random.choice(pool)


def idle_chatter_for_mood(happiness: int) -> str:
    if happiness >= 65:
        return pick(IDLE_CHATTER_HAPPY)
    elif happiness >= 35:
        return pick(IDLE_CHATTER_NEUTRAL)
    else:
        return pick(IDLE_CHATTER_SAD)
