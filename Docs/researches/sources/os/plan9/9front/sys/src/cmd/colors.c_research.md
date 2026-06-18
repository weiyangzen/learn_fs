# File Research: sources/os/plan9/9front/sys/src/cmd/colors.c

Graphical color-map viewer for Plan 9 draw/event. It displays the screen color map or a grayscale ramp in a grid and reports color values under mouse selection.

Flags: `-r` shows a grey ramp instead of `cmap2rgb`, and `-x` formats displayed values in hex.

`eresized` lays out color rectangles based on screen depth: up to 256 colors, 16 columns for depth > 8, or a depth-derived grid for lower depths. It redraws all swatches after resize.

For grayscale on `CMAP8`, it builds a dithered 4x4 image using a Bayer-like threshold table to approximate finer grey levels.

Left mouse drag prints selected index and RGBA-derived value at the top of the window. Right mouse menu supports exit.
