# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/cfill.c

`cfill.c` sets the current background/fill color. It parses a color string with `bcolor()` and updates `e1->backgr` only when the parsed value is non-negative.
