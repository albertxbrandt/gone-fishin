"""The area under the story that holds the choice buttons (or the name box)."""

import tkinter as tk

from gone_fishin.ui import theme

MIN_COLUMNS = 3
MAX_ROWS = 2  # extra options add columns instead of a third row


class OptionBar(tk.Frame):
    """Shows choice buttons in a grid, a text entry for the player's name, or nothing."""

    def __init__(self, parent):
        super().__init__(parent, bg=theme.BG)
        self._columns = 0
        self._set_columns(MIN_COLUMNS)

    def _set_columns(self, count):
        """Make the first `count` grid columns share the width equally and switch off any extras."""
        for col in range(max(count, self._columns)):
            used = col < count
            # uniform="option" forces every used column to the same width.
            self.columnconfigure(col, weight=1 if used else 0, uniform="option" if used else "")
        self._columns = count

    def _clear(self):
        """Remove the current buttons and let the bar resize to fit what's added next."""
        self.grid_propagate(True)
        for widget in self.winfo_children():
            widget.destroy()

    def _make_button(self, label, command):
        """A flat, colored button that lightens when the mouse is over it."""
        button = tk.Button(
            self, text=label, command=command, font=theme.BUTTON_FONT,
            bg=theme.BUTTON_BG, fg=theme.BUTTON_TEXT, activebackground=theme.BUTTON_HOVER,
            activeforeground=theme.BUTTON_TEXT, relief="flat", bd=0, pady=8, cursor="hand2",
        )
        button.bind("<Enter>", lambda _: button.configure(bg=theme.BUTTON_HOVER))
        button.bind("<Leave>", lambda _: button.configure(bg=theme.BUTTON_BG))
        return button

    def show_options(self, options, on_choose):
        """Lay out one button per option, left to right, in at most MAX_ROWS rows."""
        self._clear()
        # -(-a // b) rounds the division up, e.g. 7 options over 2 rows -> 4 columns.
        columns = max(MIN_COLUMNS, -(-len(options) // MAX_ROWS))
        self._set_columns(columns)
        for i, option in enumerate(options):
            button = self._make_button(option.label, lambda o=option: on_choose(o))
            button.grid(row=i // columns, column=i % columns, sticky="ew", padx=5, pady=5)

    def show_text_input(self, button_label, on_submit):
        """A text box plus a submit button. Pressing Enter also submits."""
        self._clear()
        self._set_columns(MIN_COLUMNS)
        entry = tk.Entry(self, font=theme.STORY_FONT, bg=theme.LOG_BG, fg=theme.TEXT,
                         insertbackground=theme.TEXT, relief="flat")
        entry.grid(row=0, column=0, columnspan=MIN_COLUMNS - 1, sticky="ew", padx=5, pady=5, ipady=8)
        entry.bind("<Return>", lambda _: on_submit(entry.get()))
        entry.focus_set()
        self._make_button(button_label, lambda: on_submit(entry.get())).grid(
            row=0, column=MIN_COLUMNS - 1, sticky="ew", padx=5, pady=5)

    def show_nothing(self):
        """Hide the controls but keep their space so the story area doesn't jump."""
        height = self.winfo_height()
        self._clear()
        self.configure(height=height)
        self.grid_propagate(False)
