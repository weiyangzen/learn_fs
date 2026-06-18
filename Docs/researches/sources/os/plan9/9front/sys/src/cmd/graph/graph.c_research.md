# File Research: sources/os/plan9/9front/sys/src/cmd/graph/graph.c

Standalone plotting command using the simple `iplot` output protocol. It reads x/y data from stdin, supports automatic x values, overlays, labels, line modes, symbols, grid style, transpose, equal scaling, explicit/log axes, sizing/offsets, and pen color cycling.

The program computes data limits, expands linear/log scales to usable tick quanta, maps values into a 4096x4096 plotting coordinate range, draws axes/grid/ticks, plots connected or disconnected series, emits optional labels/symbols, and prints an axis/title summary. It uses global state heavily and emits plotting commands through macros in `iplot.h`.
