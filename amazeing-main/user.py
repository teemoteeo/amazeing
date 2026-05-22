#!/usr/bin/env python3
"""user.py — thin entry point: parse config, launch curses TUI."""

from maze_parser import parse_input
from generator import MazeGenerator
from visual import Visualinho


def user() -> None:
    config = parse_input("config.txt")
    maze   = MazeGenerator(config)
    vis    = Visualinho(maze)
    vis.run(config)

