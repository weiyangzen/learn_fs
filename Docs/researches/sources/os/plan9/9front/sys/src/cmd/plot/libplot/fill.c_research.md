# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/fill.c

`fill.c` implements polygon filling with a scanline edge table. It builds active edges from one or more polygons, clips to the screen rectangle, tracks winding transitions, and draws horizontal spans using Plan 9 `line()` calls.

The exported `fill()` uses the odd winding rule and the current foreground color. The implementation allocates edge and scanline lists per fill call and includes legacy conditional code around an old “BART_BUG_FIXED” span drawing path.
