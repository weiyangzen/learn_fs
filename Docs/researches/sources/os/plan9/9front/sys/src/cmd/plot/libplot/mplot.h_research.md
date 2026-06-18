# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/mplot.h

`mplot.h` defines libplot’s Plan 9 drawing environment. It includes Plan 9 libc/draw/event headers, coordinate conversion macros, the `penvir` environment structure, clipping and mapping globals, segment support structures, and prototypes for public plot and backend functions.

The active environment pointers `e0`, `e1`, and `esave` are shared across libplot files.
