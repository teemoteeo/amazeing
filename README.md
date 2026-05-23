*This project has been created as part of the 42 curriculum by tcostant, acentron.*

# A-MAZE-ING

```
 █████╗  ███╗   ███╗ █████╗ ███████╗███████╗ ██╗███╗   ██╗ ██████╗
██╔══██╗ ████╗ ████║██╔══██╗╚══███╔╝██╔════╝ ██║████╗  ██║██╔════╝
███████║ ██╔████╔██║███████║  ███╔╝ █████╗   ██║██╔██╗ ██║██║  ███╗
██╔══██║ ██║╚██╔╝██║██╔══██║ ███╔╝  ██╔══╝   ██║██║╚██╗██║██║   ██║
██║  ██║ ██║ ╚═╝ ██║██║  ██║███████╗███████╗ ██║██║ ╚████║╚██████╔╝
╚═╝  ╚═╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝
```


## Description

A-MAZE-ING is a terminal maze generator and visualiser written in Python.
It reads a plain-text config file, generates a maze using one of three
carving algorithms (DFS, Prim, or Kruskal), solves it with BFS, and draws
it directly in the terminal using ANSI escape codes and box-drawing
characters. An interactive numbered menu lets you regenerate, change
algorithm, toggle perfect mode, show/hide the animated solution, and
customise colours and dimensions — all at runtime.

A standalone pip-installable package (`mazegen`) ships alongside the main
project. It exposes a clean `MazeGenerator` class that any Python project
can import without pulling in the rest of the codebase.


## Instructions

```bash
make install        # pip install -r requirements.txt
make run            # python3 a_maze_ing.py config.txt
make debug          # pdb session
make lint           # flake8 + mypy (strict)
make test           # pytest tests/
make clean          # remove __pycache__, .mypy_cache, *.pyc
make package        # build mazegen wheel + tarball
```


## Config file format

The config file uses a simple `KEY=VALUE` format. Lines starting with `#`
and blank lines are ignored. All keys are required except `SEED` and
`ALGORITHM`.

```
# Example config.txt
WIDTH=20
HEIGHT=20
ENTRY=0,0
EXIT=19,19
OUTPUT_FILE=maze.txt
PERFECT=TRUE
SEED=
ALGORITHM=DFS
```

### Keys

| Key           | Type      | Description                                                        |
|---------------|-----------|--------------------------------------------------------------------|
| `WIDTH`       | int > 0   | Maze width in cells                                                |
| `HEIGHT`      | int > 0   | Maze height in cells                                               |
| `ENTRY`       | `x,y`     | Entry cell coordinates (zero-indexed, inside the grid)             |
| `EXIT`        | `x,y`     | Exit cell coordinates (zero-indexed, inside the grid, ≠ ENTRY)     |
| `OUTPUT_FILE` | string    | Path of the output file written after each generation              |
| `PERFECT`     | `TRUE` / `FALSE` | `TRUE` → one unique path; `FALSE` → ~15% of internal walls broken |
| `SEED`        | int or empty | Optional RNG seed for reproducible mazes; leave blank for random |
| `ALGORITHM`   | `DFS` / `PRIM` / `KRUSKAL` | Carving algorithm (default: `DFS`)            |

### Validation rules

- `WIDTH` and `HEIGHT` must be > 0.
- `ENTRY` and `EXIT` must be inside the grid and must differ.
- An invalid algorithm string raises `ValueError` at parse time.
- Malformed lines (no `=`) raise `ValueError` with the line number.


## Interactive menu

After generation the program drops into a numbered text menu redrawn above
the maze on every action:

```
--- MAZE MENU ---
1. Generate new maze
2. Pick algo
3. Perfect Maze on/off
4. Show solution
5. Hide solution
6. Change maze colors and settings
7. Quit
```

| Choice | Action |
|--------|--------|
| `1` | Regenerate with current config and animate the carving |
| `2` | Pick algorithm: 1 DFS · 2 Prim · 3 Kruskal, then regenerate |
| `3` | Toggle `PERFECT` flag and regenerate |
| `4` | Animate BFS solution path (box-drawing connectors + ♘ at exit) |
| `5` | Hide solution overlay |
| `6` | Open colour / size / entry-exit sub-menu (see below) |
| `7` or `q` | Quit |

### Sub-menu 6 — colours and settings

| Sub-choice | Action |
|------------|--------|
| `1` | Change wall colour: 1 Green · 2 Yellow · 3 Red · 4 Blue |
| `2` | Change "42" pattern colour: same four options |
| `3` | Set new width and height (min 8, max 25). Exit coords are clamped automatically |
| `4` | Set new entry and exit coordinates (`x, y` format). Validated before applying |
| `5` | Back to main menu |


## Output file format

Written to `OUTPUT_FILE` after every generation or setting change.

```
<WIDTH hex digits per row>   ← HEIGHT rows
                             ← blank line
<entry_x>,<entry_y>
<exit_x>,<exit_y>
<path>
```

- **Grid rows:** one uppercase hex digit per cell, top-to-bottom.
- **Cell encoding:** 4-bit nibble — each bit is a closed wall.
  `N=bit0 (1)`, `E=bit1 (2)`, `S=bit2 (4)`, `W=bit3 (8)`.
  `0xF` = all four walls closed. `0x0` = all open.
- **Path:** consecutive `N`/`E`/`S`/`W` letters from entry to exit
  (shortest path via BFS). Empty if no path exists.

### Example — 5 × 4 maze

```
9554C
3CD45
9645C
3EDE6

0,0
4,3
EESSESS
```

`9` = `0b1001` = N + W closed (top-left corner).
`6` = `0b0110` = E + S closed.


## Cell encoding reference

| Bit | Value | Wall |
|-----|-------|------|
|  0  |   1   | North |
|  1  |   2   | East  |
|  2  |   4   | South |
|  3  |   8   | West  |


## Maze generation algorithm

### Which algorithm and why

The **default** algorithm is **randomised iterative Depth-First Search
(DFS)**, sometimes called the "recursive backtracker".

We chose it as the default because:

- It produces mazes with **long, winding corridors** and a single
  pronounced solution path — visually striking and immediately
  readable.
- The iterative stack-based implementation avoids Python's recursion
  limit even for large grids.
- It is conceptually the simplest of the three, making the code easy
  to follow and extend.

Two additional algorithms are available:

**Randomised Prim's** — maintains a frontier of candidate walls
between visited and unvisited cells. At each step a random wall is
picked; if the unvisited side is still unvisited the wall is carved.
This produces mazes with more branches and shorter average dead-ends,
giving a "bushier" texture compared to DFS.

**Randomised Kruskal's** — builds the complete list of internal edges,
shuffles it, then walks the list with a Union-Find structure (path
compression + union by rank). An edge is carved whenever its two
endpoints belong to different components. The result is a statistically
uniform spanning tree — passages are distributed more evenly across
the grid.

### Non-perfect mode (`PERFECT=FALSE`)

After the spanning-tree carve, ~15% of the remaining internal walls
(excluding border walls and walls adjacent to the "42" pattern) are
randomly removed. This introduces cycles so that multiple paths exist
between any two cells.

### "42" pattern

When the maze is at least 11 × 11 cells, a "42" silhouette is
embedded at centre before carving. The pattern cells are pre-marked as
visited so every algorithm skips them, leaving them as solid walls.
The pattern is not placed if it would overlap the entry or exit cell,
or if the maze is too small.


## Reusable components

### `mazegen` package

The file `mazegen.py` is a **self-contained, zero-dependency** Python
module that can be installed as a pip package:

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

```python
from mazegen import MazeGenerator

maze = MazeGenerator(
    width=20, height=15,
    entry=(0, 0), exit=(19, 14),
    seed=42,
)
print(maze.grid)      # list[list[int]]  — grid[y][x], nibble per cell
print(maze.solution)  # 'NNEESS...'      — shortest path letters
maze.write_output('maze.txt')
maze.print_ascii()    # quick ASCII preview
```

It uses only the standard library (`random`, `collections`, `sys`)
and implements DFS generation + BFS solving. It is entirely
independent from `generator.py`, `visual.py`, `solver.py`, and
`user.py` — you can drop the wheel into any Python 3.10+ project.

### `generator.MazeGenerator`

The main `MazeGenerator` class (in `generator.py`) is also reusable
independently of the UI:

```python
from maze_parser import parse_input
from generator import MazeGenerator

config = parse_input("config.txt")
maze = MazeGenerator(config)
print(maze.grid)          # list[list[int]]
maze.write_output("out.txt")
```

`carve_steps` and `knock_steps` are public lists of wall-removal
events that can be replayed by any renderer (not just `Visualinho`).

### `solver.MazeSolver`

```python
from solver import MazeSolver

solver = MazeSolver(maze)
path = solver.bfs(maze.entry, maze.exit)  # list[(x, y)]
```

`MazeSolver` depends only on `generator.grid`, `width`, and `height`.
It can be used with any object that exposes those three attributes.

### `maze_parser.MazeConfig` + `parse_input`

`MazeConfig` is a plain dataclass-style object. `parse_input` returns
a validated `MazeConfig` from any `KEY=VALUE` text file following the
format above. Both can be reused to add new frontends (e.g. a web API
or a GUI) without touching generation logic.


## Project structure

```
a_maze_ing.py      Entry point — argument parsing, wires config → user()
generator.py       MazeGenerator: DFS / Prim / Kruskal + "42" pattern
                   + non-perfect mode + BFS output path
maze_parser.py     parse_input() + MazeConfig (config file → validated object)
solver.py          MazeSolver: BFS path as list of (x, y) coordinates
visual.py          Visualinho: ANSI terminal renderer + animated carving
                   + animated solution path
user.py            Interactive menu loop — ties all modules together
mazegen.py         Standalone pip package (DFS only, zero dependencies)
config.txt         Default config file
maze.txt           Last generated output (overwritten on each run)
pyproject.toml     Build metadata for the mazegen wheel
requirements.txt   Dev dependencies (flake8, mypy, pytest, build)
Makefile           Convenience targets: install / run / lint / test / package
```


## Team & project management

### Roles

| Member   | Responsibilities |
|----------|-----------------|
| tcostant | Core maze generation (`generator.py`): DFS, Prim, Kruskal, "42" pattern, non-perfect mode, BFS output path. `mazegen` standalone package. Config parser (`maze_parser.py`). Entry point (`a_maze_ing.py`). |
| acentron | Terminal visualiser (`visual.py`): ANSI renderer, box-drawing walls, path animation, carving animation. Interactive menu (`user.py`): all runtime controls, colour picker, dimension/entry-exit editing. `solver.py`. |

### Planning and how it evolved

**Initial plan:** implement a basic DFS generator writing a hex grid to
file, add a simple terminal visualiser, and deliver on time.

**How it evolved:**

- We added Prim and Kruskal relatively early once DFS was stable, because
  the algorithm selection was in the spec and the Union-Find + frontier
  abstractions were interesting to build.
- The "42" pattern started as a fun stretch goal and ended up requiring a
  pre-pass over the grid before carving — which led to the `_pattern_cells`
  / `_visited` pre-marking design used by all three algorithms.
- The standalone `mazegen` package was not in the original plan; we added
  it after realising the generator core had no UI dependencies and could
  be shipped cleanly.
- The animated carving (`animate_generation`) was added late because we
  noticed `carve_steps` was already being recorded and replaying it was
  almost free.
- The interactive menu grew organically: colour picking and
  dimension/entry-exit editing were added after basic regen and algo
  switching worked.

### What worked well

- Keeping generation (`generator.py`), solving (`solver.py`), rendering
  (`visual.py`), and the menu loop (`user.py`) in separate modules made
  it easy to work in parallel without conflicts.
- Recording `carve_steps` and `knock_steps` as lists of events gave us
  animation for free with no changes to the core logic.
- The nibble encoding (one hex digit per cell, 4 bits = 4 walls) is
  compact, directly writable to the output file, and easy to manipulate
  with bitwise ops.
- Type annotations throughout the codebase made `mypy` useful as a
  lightweight test layer.

### What could be improved

- `user.py` hardcodes `config.txt` instead of using the path passed on
  the command line — a late oversight we did not get to fix.
- The interactive menu is a plain numbered list; a full `curses` TUI with
  arrow-key navigation would be more ergonomic on large terminals.
- There are no automated tests for `visual.py` and `user.py` (terminal
  output is hard to unit-test without mocking).
- The `trextre()` post-processing step in `generator.py` fixes a rare
  isolated-cell edge case but is undocumented and should be either
  properly explained or absorbed into the carving logic.

### Tools used

| Tool | Purpose |
|------|---------|
| **Python 3.10+** | Primary language |
| **flake8** | PEP 8 style linting |
| **mypy** | Static type checking (strict mode) |
| **pytest** | Unit testing |
| **build / setuptools** | Packaging `mazegen` as a wheel |
| **pyfiglet** | ASCII art banner (imported but rendered at terminal level) |
| **Git** | Version control |
| **GitHub Copilot / ChatGPT** | Used for boilerplate suggestions and documentation drafts; all output reviewed, tested, and validated by both team members |


## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive backtracker (DFS) — jamisbuck.org](http://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracker)
- [Prim's algorithm — jamisbuck.org](http://weblog.jamisbuck.org/2011/1/10/maze-generation-prim-s-algorithm)
- [Kruskal's algorithm — jamisbuck.org](http://weblog.jamisbuck.org/2011/1/3/maze-generation-kruskal-s-algorithm)
- [Disjoint Set Union (Union-Find) — cp-algorithms.com](https://cp-algorithms.com/data_structures/disjoint_set_union.html)
- [BFS — cp-algorithms.com](https://cp-algorithms.com/graph/bfs.html)
- [ANSI escape codes — Wikipedia](https://en.wikipedia.org/wiki/ANSI_escape_code)
- [Python packaging tutorial — packaging.python.org](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
