# File Research: sources/os/plan9/plan9/sys/src/cmd/colors.c

Graphical color-map viewer. Displays available color cells as a grid sized to screen depth; for true-color displays it shows 256 entries. Options: `-x` prints selected values in hex, `-r` displays a grey ramp instead of Plan 9 color-map colors.

In ramp mode on `CMAP8`, it dithers 4x4 grey cells with a Bayer-like matrix. Left mouse drag over a cell updates text with index and RGB/ARGB value. Right-button menu exits. Resizing recomputes grid rectangles and redraws.
