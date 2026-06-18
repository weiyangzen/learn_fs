# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/ppause.c

Interactive pause helper for plot.

Key responsibilities:
- Flushes stdout.
- Reads up to four bytes from stdin.
- Clears the plot window with `erase()`.

Notable behavior:
- Input contents are ignored; any read wakes the plot.
