# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/fill.c

Scanline polygon filler for libplot.

Key responsibilities:
- Converts lists of polygon vertices to screen-space active edges.
- Clips vertical extents to the screen rectangle.
- Fills scanline spans using an odd winding rule.
- Maintains incremental edge x positions using integer Bresenham-style fractions.
- Draws horizontal filled spans with Plan 9 draw `line()`.

Important behavior:
- Supports multiple contours through `cnt[]` and `pts[]`.
- Ignores horizontal edges.
- Uses `screen->r` bounds rather than libplot’s `clipmin` rectangle.
- `fill()` always calls the internal polygon routine with `Odd` and current foreground color.

Dependencies:
- Uses `SCX`, `SCY`, `getcolor()`, `screen`, and Plan 9 `Point` helpers.

Notable risks:
- Allocation size is based on total vertex count; malformed counts could stress memory.
- The declared `Nonzero` winding rule is unused.
- Filling is screen-rectangle clipped, not the libplot clipping rectangle used by `vec()`.
