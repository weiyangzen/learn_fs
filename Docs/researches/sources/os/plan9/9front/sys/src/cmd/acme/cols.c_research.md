# File Research: sources/os/plan9/9front/sys/src/cmd/acme/cols.c

This file manages Acme columns and the windows inside them.

Key responsibilities:
- `colinit()` initializes a column tag and draws its controls (`New Cut Paste Snarf Sort Zerox Delcol`).
- `coladd()` inserts a new or existing window into a column, splitting available vertical space.
- `colclose()` removes a window and expands neighboring windows into the freed area.
- `colcloseall()` closes all windows and frees the column.
- `colresize()` resizes the column and proportionally resizes windows.
- `colsort()` sorts windows by file name and lays them out.
- `colgrow()` expands a window, makes it full-column, or repacks surrounding windows based on button action.
- `coldragwin()` handles moving/resizing windows by mouse drag, including moving across columns.
- `colwhich()` maps a point to a column tag, window tag, body, or scroll area.
- `colclean()` checks whether every window in the column is clean.

Important dependencies:
- Calls window functions (`wininit`, `winresize`, `winclose`, `windelete`, `winclean`), text functions, row hit testing, and mouse helpers.
- Uses draw primitives to repaint background and borders.

Filesystem/storage relevance:
- Indirect: columns own windows, and windows expose files through Acme's synthetic 9P namespace. Column operations can close windows and therefore release file references.

Notes:
- `c->safe` tracks whether the layout is fully packed or temporarily obscured by a full-column window.
- Window creation here does not always log itself; callers are responsible for `xfidlog(..., "new")` except in specific flows.
