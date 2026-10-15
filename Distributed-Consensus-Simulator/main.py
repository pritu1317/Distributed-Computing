"""
main.py
-------
Entry point of the Distributed Consensus Simulator.

Run with:
    python main.py
"""

import customtkinter as ctk

from config import (
    APP_TITLE,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from gui.dashboard import Dashboard


def main():
    # Modern CustomTkinter look: light appearance, blue color theme
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # Create and configure the main window
    app = Dashboard()
    app.title(APP_TITLE)
    app.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    app.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

    # Start the Tkinter event loop
    app.mainloop()


if __name__ == "__main__":
    main()
