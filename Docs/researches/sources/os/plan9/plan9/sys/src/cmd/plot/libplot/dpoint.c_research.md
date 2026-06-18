# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/dpoint.c

Draws a one-pixel point and moves the current plot position.

Key responsibilities:
- Draws a 1x1 rectangle at the scaled coordinate.
- Uses current foreground color.
- Calls `move()` to update `e1->copyx/copyy`.

Notable behavior:
- Does not explicitly clip; draw clipping is handled by the image rectangle.
