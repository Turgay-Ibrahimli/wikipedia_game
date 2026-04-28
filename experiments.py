"""
Convenience wrapper for running the built-in experiment suite.

This is equivalent to:
  python wikipedia_game/main.py --experiments --all-algorithms
"""

from __future__ import annotations

from main import main


if __name__ == "__main__":
    raise SystemExit(main(["--experiments", "--all-algorithms"]))
