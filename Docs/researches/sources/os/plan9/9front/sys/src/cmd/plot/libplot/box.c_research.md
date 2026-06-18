# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/box.c

`box.c` draws an outline rectangle by moving to one corner and issuing four `vec()` calls around the perimeter. It relies on the current libplot coordinate transform and foreground color.
