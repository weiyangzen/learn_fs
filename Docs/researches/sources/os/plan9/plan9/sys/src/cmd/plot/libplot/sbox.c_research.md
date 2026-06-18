# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/sbox.c

Clears a rectangular region in plot coordinates.

Key responsibilities:
- Converts rectangle corners to screen coordinates.
- Normalizes corner order.
- Clips to libplot clipping bounds.
- Clears the rectangle using current background color.

Important behavior:
- Empty clipped rectangles are ignored.
