"""The fishing rods sold in the shop."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Rod:
    rod_id: int  # row in rod_table
    name: str
    price: int
    luck: float  # multiplies a catch's chance once per rarity tier above Common
    description: str


# Cheapest to best. The free Basic Rod is the one every player starts with.
RODS = (
    Rod(1, "Basic Rod", 0, 1.0, "The trusty starter rod the dockmaster gave you."),
    Rod(2, "Fiberglass Rod", 75, 1.3, "Light and bendy. A solid step up from the starter rod."),
    Rod(3, "Carbon Rod", 300, 1.7, "Stiff, sensitive, and strong enough for river monsters."),
    Rod(4, "Golden Rod", 1000, 2.2, "Legend says the fish come to it."),
)


def best_rod(owned_ids):
    """The luckiest rod the player owns. Players always fish with their best rod."""
    owned = [rod for rod in RODS if rod.price == 0 or rod.rod_id in owned_ids]
    return max(owned, key=lambda rod: rod.luck)


def upgrades(current):
    """Rods better than the one the player has (the only ones the shop offers)."""
    return [rod for rod in RODS if rod.luck > current.luck]
