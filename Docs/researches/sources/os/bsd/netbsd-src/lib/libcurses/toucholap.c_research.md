# File Research: sources/os/bsd/netbsd-src/lib/libcurses/toucholap.c

Implements `touchoverlap(WINDOW *win1, WINDOW *win2)`.

It computes the screen-coordinate rectangle where two windows overlap, converts that rectangle into `win2` coordinates, and touches each overlapping line range in `win2` so a later refresh repaints that area.
