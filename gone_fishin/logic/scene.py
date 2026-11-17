"""The two types the game logic hands to the UI.

A Scene is one step of the story: the text to type out and the buttons to show
under it. The UI never decides what happens next. It just shows the Scene and
calls the action of whichever Option the player clicks.
"""

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Option:
    """One button: its label, and a function that runs when clicked and returns the next Scene."""
    label: str
    action: Callable[[], "Scene"]


@dataclass
class Scene:
    text: str
    options: list = field(default_factory=list)
    asks_name: bool = False  # show a text box for the player's name instead of buttons
    is_final: bool = False   # the game is over; the window closes after this text
    delay_ms: int = 0        # wait this long after the text finishes typing, then show follow_up
    follow_up: Callable[[], "Scene"] | None = None  # the Scene that arrives after the wait
    cancel: Callable[[], "Scene"] | None = None     # shown as a button during the wait; skips follow_up
