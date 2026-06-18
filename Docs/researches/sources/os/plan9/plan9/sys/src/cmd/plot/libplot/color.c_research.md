# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/color.c

Sets the plot foreground color.

Key responsibilities:
- Converts the supplied color string with `bcolor()`.
- Stores the result in `e1->foregr`.

Notable risks:
- Unlike `cfill()`, it stores negative side-effect return values, which can later be passed to `getcolor()`.
