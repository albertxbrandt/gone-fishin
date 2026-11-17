"""The Village Shop scenes: sell your catch, ask about rods, and buy them."""

from gone_fishin.data import inventory, transactions
from gone_fishin.logic import fishing, rods, shop_narration as narration
from gone_fishin.logic.locations import LOCATIONS, RARE
from gone_fishin.logic.scene import Option, Scene

# Spots with Rare or Legendary fish; the Pond has none, so rods don't matter there.
RARE_SPOTS = [loc for loc in LOCATIONS.values() if any(c.rarity >= RARE for c in loc.catches)]


class Shop:
    """Builds the shop's Scenes for one player. `leave` returns the Scene to go back to (the dock)."""

    def __init__(self, player_id, leave):
        self.player_id = player_id
        self.leave = leave
        # Rods only change when bought here, so look up the player's rod once and remember it.
        self._rod = rods.best_rod(transactions.purchased_rod_ids(player_id))

    def current_rod(self):
        return self._rod

    def enter(self, message=None):
        """The shop counter. After a sale or purchase, `message` replaces the long welcome text."""
        coins = transactions.balance(self.player_id)
        if message:
            text = message + "\n" + narration.shop_balance(coins)
        else:
            text = narration.shop_counter(coins, self._rod)

        options = []
        unsold = inventory.list_unsold(self.player_id)
        if unsold:
            options.append(Option(f"Sell All ({len(unsold)} items)", self._sell_all))
        for upgrade in rods.upgrades(self._rod):
            options.append(Option(f"Ask about {upgrade.name}", lambda r=upgrade: self._ask_about(r)))
        options.append(Option("Leave Shop", self.leave))
        return Scene(text, options)

    def _ask_about(self, rod):
        """Details page for one rod, comparing rare-catch odds with the player's current rod."""
        odds = [
            (loc.name, fishing.rare_or_better_chance(loc, self._rod), fishing.rare_or_better_chance(loc, rod))
            for loc in RARE_SPOTS
        ]
        return Scene(narration.rod_details(rod, self._rod, odds), [
            Option(f"Buy {rod.name} ({rod.price}c)", lambda: self._buy(rod)),
            Option("Back to Counter", self.enter),
        ])

    def _sell_all(self):
        """Sell every item in the bag at its listed value."""
        sales = [
            (inventory_id, item_id, value)
            for inventory_id, item_id, _, _, value in inventory.list_unsold(self.player_id)
        ]
        earned = transactions.sell_items(self.player_id, sales)
        return self.enter(narration.sold(len(sales), earned))

    def _buy(self, rod):
        """Buy a rod if the player can afford it. It's equipped right away."""
        coins = transactions.balance(self.player_id)
        if coins < rod.price:
            return self.enter(narration.cannot_afford(rod, coins))
        transactions.buy_rod(self.player_id, rod.rod_id, rod.price)
        self._rod = rod
        return self.enter(narration.bought(rod))
