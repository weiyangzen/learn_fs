# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/cfill.c

Sets the plot background/fill color.

Key responsibilities:
- Converts a color string with `bcolor()`.
- Stores successful colors in `e1->backgr`.

Notable behavior:
- Negative `bcolor()` results are ignored, because those strings may encode side effects such as pattern or slant settings.
