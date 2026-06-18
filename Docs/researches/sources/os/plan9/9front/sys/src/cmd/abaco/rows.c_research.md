# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/rows.c

Top-level row and column management for Abaco.

Key responsibilities:
- Initializes the root row tag and starting rectangle.
- Adds columns by splitting existing column rectangles.
- Resizes all columns proportionally on screen resize.
- Drags columns to reorder or resize adjacent column boundaries.
- Closes columns and expands neighbors into freed space.
- Locates columns/text by point for event dispatch.

Important behavior:
- Default new column steals about 40% of the last column.
- Column additions enforce rough minimum widths.
- Dragging a column can shuffle it before/after other columns or resize its left neighbor.
- The row tag contains top-level commands `Newcol Google Exit`.

Dependencies:
- Uses `Column`, `Text`, draw primitives, mouse state, and column APIs.

Notable risks:
- Manual width constraints are heuristic and can still produce cramped layouts on small screens.
