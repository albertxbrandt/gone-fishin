"""Rolling the dice for a cast."""

import random
from dataclasses import dataclass
from functools import lru_cache

from gone_fishin.logic.locations import RARE

# How long the player waits for a bite, in milliseconds.
MIN_BITE_MS, MAX_BITE_MS = 3000, 20000


@dataclass(frozen=True)
class Outcome:
    """The result of one cast, ready to be saved and narrated."""
    event_type: int
    item_id: int | None
    item_name: str | None
    weight_lb: float | None
    rarity: int
    value: int


@lru_cache(maxsize=None)
def _weights(location, rod):
    """Odds of each catch at this spot with this rod.

    Each catch's base chance is multiplied by the rod's luck once per rarity
    tier, e.g. a Rare catch (tier 2) with luck 1.7 becomes 1.7 * 1.7 = 2.89x as
    likely. Common catches (tier 0) are unchanged. There are only a few spots
    and rods, so each combination is worked out once and remembered (lru_cache).
    """
    return tuple(c.chance * rod.luck ** c.rarity for c in location.catches)


def bite_delay():
    """A random wait between casts, from MIN_BITE_MS to MAX_BITE_MS milliseconds."""
    return random.randint(MIN_BITE_MS, MAX_BITE_MS)


def cast_line(location, rod):
    """Pick a random catch using the rod-adjusted odds and give it a random weight."""
    catch = random.choices(location.catches, weights=_weights(location, rod))[0]
    weight = round(random.uniform(catch.min_lb, catch.max_lb), 1) if catch.item_name else None
    return Outcome(catch.event_type, catch.item_id, catch.item_name, weight, catch.rarity, catch.value)


def rare_or_better_chance(location, rod):
    """Chance (0 to 1) that a cast here lands a Rare or Legendary catch. Shown in the shop."""
    weights = _weights(location, rod)
    rare = sum(w for c, w in zip(location.catches, weights) if c.rarity >= RARE)
    return rare / sum(weights)
