# File Research: sources/os/plan9/plan9/sys/src/cmd/winwatch.c

This is a graphical window watcher for Plan 9 rio windows.

Behavior:
- Periodically reads `/dev/wsys`, opens each window's `label`, filters by optional exclusion regexp, and maintains an array of `Win` entries.
- Displays each window label in a tiled grid.
- Right-click selection on a label writes `unhide`, `top`, and `current` to that window's `wctl`, bringing it forward.
- Keyboard `q` or delete exits.

Layout/rendering:
- Uses configurable font, default `/lib/font/bit/lucidasans/unicode.8.font`.
- Computes rows from screen height and columns from number of windows.
- Draws labels in light blue rectangles with black borders.
- Incremental redraw uses `dirty` flags and clears removed slots.

Options:
- `-e exclude`: regexp against labels to hide entries.
- `-f font`: font path.

Notable behavior:
- The refresh logic assumes `/dev/wsys` directory entries come in stable ordering; it compares by position and label to avoid redrawing.
- Labels are truncated to the fixed 128-byte read buffer.
