"""The scrolling story area with the typewriter effect and blinking cursor.

While a cast is waiting, a one-line ASCII meter is drawn under the story and
rewritten in place until the bite lands or the player pulls the line in.
"""

import time
import tkinter as tk
from collections import deque

from gone_fishin.ui import theme

CHARS_PER_TICK = 3  # characters typed per step
TICK_MS = 10        # delay between steps (about 300 characters per second)
BLINK_MS = 530      # cursor blink speed, similar to a normal text cursor
MAX_LINES = 400     # older lines are removed past this so long sessions stay fast
CURSOR = "|"
# "end-2c" sits just before the cursor character (the Text widget keeps a trailing newline after it).
BEFORE_CURSOR = "end-2c"

METER_WIDTH = 20    # characters inside the brackets of the bite meter
METER_TICK_MS = 100  # how often the meter checks whether another mark is due


def ascii_meter(fraction):
    """A text meter, from `[>...................]` at the start to `[====================]` when full.

    The `>` is the part still to come. fraction is 0.0 just after the cast and 1.0 when the bite is due.
    """
    filled = int(max(0.0, min(1.0, fraction)) * METER_WIDTH)
    if filled >= METER_WIDTH:
        return "[" + ("=" * METER_WIDTH) + "]"
    return "[" + ("=" * filled) + ">" + ("." * (METER_WIDTH - filled - 1)) + "]"


class StoryLog(tk.Frame):
    """Read-only story area that types messages out one after another, with a blinking cursor.

    Messages wait in a queue, so a new message never starts typing before the
    one ahead of it finishes. The cursor character always stays at the very end
    of the text, and new characters are inserted just before it.
    """

    def __init__(self, parent):
        super().__init__(parent, bg=theme.BG)
        self.text = tk.Text(
            self, bg=theme.LOG_BG, fg=theme.TEXT, font=theme.STORY_FONT, wrap="word",
            relief="flat", padx=14, pady=12, cursor="arrow",
        )
        # Tags style parts of the text: the player's choices, and the cursor.
        self.text.tag_configure("choice", foreground=theme.CHOICE_TEXT, font=theme.CHOICE_FONT)
        self.text.tag_configure("cursor", foreground=theme.TEXT)
        self.text.tag_configure("meter", foreground=theme.CHOICE_TEXT)  # the live [===>...] line
        self.text.insert("end", CURSOR, "cursor")
        self.text.configure(state="disabled")  # the player can't type into the story

        scroll = tk.Scrollbar(self, command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)
        self.text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self._queue = deque()  # messages waiting to be typed: (text, tag, on_done)
        self._typing = False
        self._has_text = False
        self._cursor_visible = True
        self._meter_after = None  # id of the meter's next redraw, so a withdraw can cancel it
        self._meter_started = 0.0
        self._meter_duration = 1
        self._meter_text = ""
        self._blink()

    def write(self, message, tag=None, on_done=None):
        """Queue a message to be typed. on_done runs once it has finished typing."""
        self._queue.append((message, tag, on_done))
        if not self._typing:
            self._next_message()

    def write_choice(self, label):
        """Echo the player's choice, styled like "> Cast Line"."""
        self.write(f"> {label}", "choice")

    def start_meter(self, duration_ms):
        """Put an ASCII meter on its own line and fill it across duration_ms milliseconds."""
        self.stop_meter()
        self._meter_duration = max(int(duration_ms), 1)
        self._meter_started = time.monotonic()
        self._set_meter(ascii_meter(0))
        self._meter_tick()

    def stop_meter(self):
        """Drop the meter line. The cast text above it stays."""
        if self._meter_after is not None:
            self.after_cancel(self._meter_after)
            self._meter_after = None
        self._meter_text = ""
        ranges = self.text.tag_ranges("meter")
        if not ranges:
            return
        self.text.configure(state="normal")
        self.text.delete(ranges[0], ranges[1])
        self.text.configure(state="disabled")

    def _meter_tick(self):
        """Advance the meter to match how much of the bite wait has passed."""
        self._meter_after = None  # this scheduled call has already started
        elapsed_ms = (time.monotonic() - self._meter_started) * 1000
        fraction = min(1.0, elapsed_ms / self._meter_duration)
        self._set_meter(ascii_meter(fraction))
        if fraction < 1:
            self._meter_after = self.after(METER_TICK_MS, self._meter_tick)

    def _set_meter(self, line):
        """Rewrite the meter line in place, so the story doesn't grow a new line every tick."""
        if line == self._meter_text:
            return
        self._meter_text = line
        self.text.configure(state="normal")
        ranges = self.text.tag_ranges("meter")
        if ranges:
            self.text.delete(ranges[0], ranges[1])
            self.text.insert(ranges[0], "\n" + line, "meter")
        else:
            self.text.insert(BEFORE_CURSOR, "\n" + line, "meter")
        self.text.configure(state="disabled")
        self.text.see("end")

    def _next_message(self):
        """Start typing the next queued message, if any."""
        if not self._queue:
            self._typing = False
            return
        self._typing = True
        self._trim_old_lines()
        message, tag, on_done = self._queue.popleft()
        if self._has_text:
            self._insert("\n\n", None)  # blank line between messages
        self._has_text = True
        self._type(message, 0, tag, on_done)

    def _type(self, message, pos, tag, on_done):
        """Type a few characters, then schedule the next few with after() so the window stays responsive."""
        self._insert(message[pos:pos + CHARS_PER_TICK], tag)
        pos += CHARS_PER_TICK
        if pos < len(message):
            self.after(TICK_MS, self._type, message, pos, tag, on_done)
            return
        if on_done:
            on_done()
        self._next_message()

    def _insert(self, chunk, tag):
        """Add text just before the cursor and scroll to the bottom."""
        self.text.configure(state="normal")
        self.text.insert(BEFORE_CURSOR, chunk, tag)
        self.text.configure(state="disabled")
        self.text.see("end")

    def _trim_old_lines(self):
        """Delete the oldest lines once the log passes MAX_LINES; a huge Text widget gets slow to update."""
        line_count = int(self.text.index("end-1c").split(".")[0])
        if line_count > MAX_LINES:
            self.text.configure(state="normal")
            self.text.delete("1.0", f"{line_count - MAX_LINES + 1}.0")
            self.text.configure(state="disabled")

    def _blink(self):
        """Toggle the cursor's color every BLINK_MS. It stays solid while text is typing."""
        self._cursor_visible = self._typing or not self._cursor_visible
        color = theme.TEXT if self._cursor_visible else theme.LOG_BG
        self.text.tag_configure("cursor", foreground=color)
        self.after(BLINK_MS, self._blink)
