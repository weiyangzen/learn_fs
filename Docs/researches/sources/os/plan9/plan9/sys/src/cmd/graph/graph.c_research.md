# File Research: sources/os/plan9/plan9/sys/src/cmd/graph/graph.c

This is the classic `graph` plotting command. It reads numeric x/y data from stdin, computes axis limits and scales, emits plot protocol commands through `iplot.h`, draws axes/grid/ticks, optional labels, and plotted lines or symbols.

Command-line options control labels, line mode, overlays, automatic abscissas, erase/overlay behavior, grid style, plotting character, transposition, equal scales, breaks, x/y limits including log scale, plot size/offset, and pen color cycling.

Scaling is handled by `getlim`, `setlim`, `setlinlim`, `setloglim`, and `scale`. `plot` iterates overlay series, converts data values to screen coordinates, draws connected vectors, emits symbols/labels, and rotates pen colors.

Notable limitations: this is old K&R-style C with custom `isdigit` and implicit-int functions, and fixed-size mark/label buffers.
