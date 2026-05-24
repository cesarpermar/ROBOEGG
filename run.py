#!/usr/bin/env python3
"""
ROBOEGG — SCARA Studio Pro
============================
Entry point for the SCARA robot control application.

Usage:
    python run.py
"""

from src.gui.studio_pro import ScaraMasterPro


def main() -> None:
    """Launch the SCARA Studio Pro application."""
    app = ScaraMasterPro()
    app.mainloop()


if __name__ == "__main__":
    main()
