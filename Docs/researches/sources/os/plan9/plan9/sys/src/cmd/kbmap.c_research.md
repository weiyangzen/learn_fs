# File Research: sources/os/plan9/plan9/sys/src/cmd/kbmap.c

This is an interactive libdraw/event utility for selecting and applying keyboard maps. By default it reads map files from `/sys/lib/kbmap`; alternatively, file names can be provided on the command line.

It builds an array of `KbMap` entries with display name, file path, rectangle, and current selection state. `geometry()` lays entries into columns based on screen size and font height, and `redraw()` paints selectable map rectangles.

`click()` handles mouse button 4 selection, confirms release over the same rectangle, writes `/sys/lib/kbmap/ascii` first as a base map, then writes the selected map to `/dev/kbmap`. The current map is highlighted and the screen is redrawn.

Filesystem relevance is direct: this utility reads keyboard map files and writes the kernel keyboard-map device. Error handling is user-visible via stderr, while allocation failures call `sysfatal`.
