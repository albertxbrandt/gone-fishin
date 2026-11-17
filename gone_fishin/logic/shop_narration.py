"""All the story text for the Village Shop."""

from gone_fishin.logic import rods


def shop_counter(coins, rod):
    """Welcome text when entering the shop: coins, current rod, and which rods are for sale."""
    upgrades = rods.upgrades(rod)
    lines = [
        "The shopkeeper looks up from behind a counter of tackle and rods.",
        f"You have {coins} coins. You're using the {rod.name} (luck x{rod.luck}).",
    ]
    if upgrades:
        lines.append("On the wall: " + ", ".join(r.name for r in upgrades) + ". Ask about one to learn more.")
    else:
        lines.append("\"You already own the finest rod in the village!\"")
    return "\n".join(lines)


def rod_details(rod, current, odds):
    """The "Ask about" page. odds is [(spot_name, current_chance, new_chance)] for a Rare-or-better catch."""
    lines = [
        f"\"Ah, the {rod.name}.\" The shopkeeper takes it down from the wall.",
        f"\"{rod.description}\"",
        "",
        f"  Price: {rod.price} coins",
        f"  Luck:  x{rod.luck}  (your {current.name}: x{current.luck})",
        "",
        "  Chance of a Rare or Legendary catch:",
    ]
    # :>4.0% formats 0.214 as " 21%"
    lines += [f"    {name:<6} {old:>4.0%}  ->  {new:>4.0%}" for name, old, new in odds]
    return "\n".join(lines)


def shop_balance(coins):
    return f"You now have {coins} coins."


def sold(count, earned):
    return f"The shopkeeper counts out {earned} coins for your {count} items."


def bought(rod):
    return f"You buy the {rod.name}! Rare fish had better watch out."


def cannot_afford(rod, coins):
    return f"The {rod.name} costs {rod.price} coins, but you only have {coins}. Keep fishing!"
