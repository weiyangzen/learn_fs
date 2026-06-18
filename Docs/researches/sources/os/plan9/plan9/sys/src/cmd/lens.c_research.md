# File Research: sources/os/plan9/plan9/sys/src/cmd/lens.c

Read fully: 268 lines, 5109 bytes. SHA-256 prefix: `cabfdd68436c1136`.

This is an interactive graphical screen magnifier. It opens `/dev/screen`, reads the screen image metadata, allocates a backing buffer and output image, then lets mouse/keyboard events choose the magnified center, zoom level, grid visibility, redraw, or exit.

Key routines:
- `drawit()` redraws the red border and magnified image.
- `makegrid()` builds an optional checker-pattern grid scaled to zoom.
- `eresized()` reattaches/resizes the window and reallocates the temporary image.
- `magnify()` reads the relevant screen rows, expands pixels by `mag`, loads scanlines into the temp image, and overlays the grid.

Dependencies: Plan 9 `draw` and `event` libraries plus `/dev/screen` layout.

Risk notes: requires screen depth of at least 8 bits and assumes bytes-per-pixel is `depth/8`. `out[8192]` bounds depend on window width and pixel depth.
