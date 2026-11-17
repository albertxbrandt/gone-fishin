"""The game engine: decides what happens after each choice.

Every method here returns a Scene (story text plus buttons). Each button's
action is another method of this class, so following the button actions traces
the whole game: start -> dock -> confirm travel -> fish -> back to dock, with
the shop branching off the dock. This file never touches Tkinter, and all
database work goes through the gone_fishin.data modules.
"""

from gone_fishin.config import HISTORY_LIMIT
from gone_fishin.data import casts, inventory, players, transactions
from gone_fishin.logic import fishing, narration
from gone_fishin.logic.locations import LOCATIONS
from gone_fishin.logic.scene import Option, Scene
from gone_fishin.logic.shop import Shop


class Game:
    """Holds who is playing and builds the next Scene for each choice."""

    def __init__(self):
        self.player_id = None
        self.player_name = None
        self.shop = None

    # ----- Starting the game -----

    def start(self):
        """First scene: pick a saved player if there are any, otherwise ask for a name."""
        names = players.list_names()
        if not names:
            return Scene(narration.welcome(), asks_name=True)
        options = [Option(name, lambda name=name: self.submit_name(name)) for name in names]
        options.append(Option("I'm New Here", self._new_player))
        return Scene(narration.welcome_returning(), options)

    def _new_player(self):
        return Scene(narration.ask_name(), asks_name=True)

    def submit_name(self, name):
        """Load or create the player, then go to the dock. Blank names are asked for again."""
        name = name.strip()
        if not name:
            return Scene(narration.name_required(), asks_name=True)
        self.player_name = name
        self.player_id, is_new = players.get_or_create(name)
        self.shop = Shop(self.player_id, leave=self._dock)
        return self._dock(narration.greeting(name, is_new))

    # ----- The dock (main menu) -----

    def _dock(self, message=None):
        """The hub scene. `message` (an inventory list, an error, etc.) is shown above the usual text."""
        coins = transactions.balance(self.player_id)
        text = (message + "\n\n" if message else "") + narration.at_dock(coins, self.shop.current_rod())
        # One button per spot, labeled with its travel fee.
        options = [
            Option(f"{loc.name} ({loc.travel_fee}c)" if loc.travel_fee else f"{loc.name} (free)",
                   lambda loc=loc: self._confirm_travel(loc))
            for loc in LOCATIONS.values()
        ]
        options += [
            Option("Inventory", self._show_inventory),
            Option("Fishing Log", self._show_history),
            Option("Village Shop", self.shop.enter),
            Option("Quit", self._quit),
        ]
        return Scene(text, options)

    def _show_inventory(self):
        return self._dock(narration.inventory(inventory.list_unsold(self.player_id)))

    def _show_history(self):
        return self._dock(narration.history(casts.recent_casts(self.player_id, HISTORY_LIMIT)))

    # ----- Traveling and fishing -----

    def _confirm_travel(self, location):
        """Confirmation screen that lists the fish at a spot before any coins are spent."""
        coins = transactions.balance(self.player_id)
        fee = f"{location.travel_fee}c" if location.travel_fee else "free"
        return Scene(narration.travel_preview(location, coins), [
            Option(f"Travel ({fee})", lambda: self._travel(location)),
            Option("Stay at Dock", self._dock),
        ])

    def _travel(self, location):
        """Charge the travel fee (if the player can afford it) and arrive at the spot."""
        if location.travel_fee:
            coins = transactions.balance(self.player_id)
            if coins < location.travel_fee:
                return self._dock(narration.cannot_afford_trip(location, coins))
            transactions.pay_travel(self.player_id, location.location_id, location.travel_fee)
        return self._at_location(location, narration.arrival(location))

    def _at_location(self, location, text):
        """Scene while standing at a spot: keep casting for free, or head back."""
        return Scene(text, [
            Option("Cast Line", lambda: self._cast(location)),
            Option("Return to Dock", self._dock),
        ])

    def _cast(self, location):
        """Roll the catch right away, then make the player wait a random few seconds for the bite."""
        outcome = fishing.cast_line(location, self.shop.current_rod())
        return Scene(
            narration.waiting_for_bite(),
            delay_ms=fishing.bite_delay(),
            follow_up=lambda: self._land(location, outcome),
            # Withdrawing wastes the cast: nothing is logged and the player stays at the spot.
            cancel=lambda: self._at_location(location, narration.withdrew_line()),
        )

    def _land(self, location, outcome):
        """The wait is over: save the catch and describe what was on the line."""
        casts.record_cast(self.player_id, location.location_id, outcome)
        return self._at_location(location, narration.cast_result(outcome, location))

    def _quit(self):
        return Scene(narration.farewell(self.player_name), is_final=True)
