"""All the story text for the main game (the shop's text is in shop_narration.py).

Keeping the wording here means game.py only decides *what* happens, and this
file decides *how it's described*. Lists use fixed-width columns, which line up
because the story log uses a monospace font.
"""

from gone_fishin.logic.locations import EVENT_TYPES, FISH, JUNK, LOCATIONS, RARITY_NAMES


INTRO = (
    "Welcome to Gone Fishin'!\n\n"
    "A quiet fishing village sits beside a pond, a lake, a river, and the open ocean."
)


# ----- Starting the game -----

def welcome():
    """Opening text when there are no saved players."""
    return INTRO + "\n" + ask_name()


def welcome_returning():
    """Opening text when there are saved players to choose from."""
    return INTRO + "\nThe dockmaster squints at you. \"Have we met before?\""


def ask_name():
    return "What is your name, angler?"


def name_required():
    return "Every angler needs a name. Please type one in."


def greeting(name, is_new):
    if is_new:
        return f"Nice to meet you, {name}. The old dockmaster hands you a fishing rod."
    return f"Welcome back, {name}. Your tackle box is right where you left it."


# ----- The dock -----

def at_dock(coins, rod):
    return (
        f"You stand on the village dock with {coins} coins and your {rod.name}.\n"
        "Where would you like to go?"
    )


def inventory(items):
    """The bag, one line per kind of item with a count, rarest first."""
    if not items:
        return "Your bag is empty. Go catch something!"
    # Rows are (inventory_id, item_id, name, rarity, value); group duplicates into one line.
    grouped = {}
    for _, _, name, rarity, value in items:
        count, _, _ = grouped.get(name, (0, rarity, value))
        grouped[name] = (count + 1, rarity, value)
    rarest_first = sorted(grouped, key=lambda name: (-grouped[name][1], -grouped[name][2]))
    lines = []
    total = 0
    for name in rarest_first:
        count, rarity, value = grouped[name]
        worth = value * count
        total += worth
        lines.append(f"  - {name:<14} x{count:<3} {RARITY_NAMES[rarity]:<10} {worth:>5}c")
    return f"You open your bag ({len(items)} items, worth {total} coins):\n" + "\n".join(lines)


def history(casts):
    """The Fishing Log: time, spot, and result of recent casts."""
    if not casts:
        return "Your fishing log is blank. You haven't cast a line yet."
    lines = [
        # timestamp[11:19] keeps just the HH:MM:SS part of "YYYY-MM-DD HH:MM:SS.mmm"
        f"  {timestamp[11:19]}  {LOCATIONS[location_id].name:<6}  {item_name or EVENT_TYPES[event_type]}"
        for timestamp, location_id, event_type, item_name in casts
    ]
    return f"Your last {len(casts)} casts:\n" + "\n".join(lines)


def farewell(name):
    return f"You pack up your rod and head home. See you next time, {name}!"


# ----- Traveling and fishing -----

def travel_preview(location, coins):
    """The "Are you sure?" travel prompt, with the spot's fish from most common to rarest."""
    question = f"Are you sure you want to travel to the {location.name}?\n"
    if location.travel_fee:
        question += f"The trip costs {location.travel_fee} coins. You have {coins}."
    else:
        question += "It's free to fish there."
    fish = sorted((c for c in location.catches if c.event_type == FISH), key=lambda c: c.rarity)
    lines = [f"  - {c.item_name:<14} {RARITY_NAMES[c.rarity]:<10} {c.value:>4}c" for c in fish]
    return question + "\nFish found here:\n" + "\n".join(lines)


def arrival(location):
    if location.travel_fee:
        return f"You pay {location.travel_fee} coins for the trip.\n{location.arrival_text}"
    return location.arrival_text


def cannot_afford_trip(location, coins):
    return (
        f"A trip to the {location.name} costs {location.travel_fee} coins, but you only have {coins}.\n"
        "The pond is free. Catch a few fish there and sell them at the shop."
    )


def waiting_for_bite():
    return "You cast your line and wait for a bite..."


def withdrew_line():
    return "You reel the line back in before anything bites."


def cast_result(outcome, location):
    """Describe a cast. Fish get a rarity tag with one '!' per tier, e.g. [Rare!!]."""
    if outcome.event_type == FISH:
        rarity = RARITY_NAMES[outcome.rarity]
        exclaim = "!" * outcome.rarity
        return (
            f"Something bites! You reel in a {outcome.item_name} weighing {outcome.weight_lb} lb.\n"
            f"[{rarity}{exclaim}] Worth {outcome.value} coins at the shop."
        )
    if outcome.event_type == JUNK:
        return f"You feel a tug... it's a {outcome.item_name}. You toss it in your bag anyway."
    return f"You wait and wait. Nothing is biting at the {location.name} right now."
