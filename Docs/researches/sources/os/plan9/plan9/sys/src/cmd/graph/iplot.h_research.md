# File Research: sources/os/plan9/plan9/sys/src/cmd/graph/iplot.h

This header maps plotting primitives to textual plot protocol commands printed on stdout. It defines macros for arcs, boxes, splines, fills, color, erase, line, move, open/close, pen, point, range, text, vectors, and related operations.

It declares `putnum` for multi-point spline/polygon data and `whoami`.

The `graph` command uses these macros as its backend abstraction.
