"""The main window, which connects the game engine to the two on-screen pieces.

The window is the story log on top and the option bar (buttons) underneath.
For each Scene from the game it:
  1. hides the buttons and clears any ASCII bite meter,
  2. types the Scene's text into the story log,
  3. when typing finishes, shows the Scene's buttons (or the name box).
A Scene that waits (a cast) types a meter like [===>...] into the story for that
wait. Withdrawing or closing the window cancels the wait, so the catch is never
saved early.
Clicking a button echoes the choice into the story and asks the game for the next Scene.
"""

import tkinter as tk

from gone_fishin.config import APP_TITLE
from gone_fishin.logic.scene import Option
from gone_fishin.ui import theme
from gone_fishin.ui.option_bar import OptionBar
from gone_fishin.ui.story_log import StoryLog

CLOSE_DELAY_MS = 2000  # how long the goodbye message stays up before the window closes


class App(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self._pending = None  # id of a scheduled follow-up scene, so it can be cancelled
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.title(APP_TITLE)
        self.geometry(theme.WINDOW_SIZE)
        self.configure(bg=theme.BG)

        # Pack the buttons first, at the bottom, so the story log can never squeeze them off-screen.
        self.options = OptionBar(self)
        self.options.pack(side="bottom", fill="x", padx=7, pady=(0, 12))
        self.log = StoryLog(self)
        self.log.pack(fill="both", expand=True, padx=12, pady=(12, 6))

        self.show(game.start())

    def show(self, scene):
        """Type out a Scene, then reveal its controls."""
        self._clear_wait()
        self.options.show_nothing()
        self.log.write(scene.text, on_done=lambda: self._show_controls(scene))

    def _show_controls(self, scene):
        if scene.follow_up:
            # A timed beat (waiting for a bite). The scheduled follow-up is dropped if the
            # player hits the cancel button or the window closes first.
            self._pending = self.after(scene.delay_ms, lambda: self.show(scene.follow_up()))
            if scene.delay_ms > 0:
                self._begin_wait(scene.delay_ms)
            if scene.cancel:
                self.options.show_options([Option("Withdraw Line", scene.cancel)], self._choose)
            return
        if scene.is_final:
            self.after(CLOSE_DELAY_MS, self.destroy)
        elif scene.asks_name:
            self.options.show_text_input("Start", self._submit_name)
        else:
            self.options.show_options(scene.options, self._choose)

    def _submit_name(self, name):
        if name.strip():
            self.log.write_choice(name.strip())
        self.show(self.game.submit_name(name))

    def _begin_wait(self, duration_ms):
        """Draw the ASCII meter for the same wait the follow-up scene is waiting on."""
        self.log.start_meter(duration_ms)

    def _clear_wait(self):
        """Remove the ASCII meter. Called whenever a new scene starts or the window closes."""
        self.log.stop_meter()

    def _on_close(self):
        if self._pending:
            self.after_cancel(self._pending)
            self._pending = None
        self._clear_wait()
        self.destroy()

    def _choose(self, option):
        """A button was clicked: echo it, then run its action to get the next Scene."""
        if self._pending:
            # A choice during a wait (Withdraw Line) replaces the scene that was scheduled.
            self.after_cancel(self._pending)
            self._pending = None
        self.log.write_choice(option.label)
        self.show(option.action())
