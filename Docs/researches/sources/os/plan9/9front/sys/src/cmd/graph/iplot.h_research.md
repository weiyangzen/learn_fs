# File Research: sources/os/plan9/9front/sys/src/cmd/graph/iplot.h

Header of plotting-output macros for graph tools. Each macro prints a compact command to stdout: open/close, range, move, vector, line, point, text, color, pen, fill, splines, boxes, circles, save/restore, etc.

It declares `putnum` for spline/poly point lists and `whoami`. The macros are a textual backend API rather than drawing directly.
