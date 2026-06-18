# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/rgb.c

Implements Plan 9 color map conversion helpers.

Key functions:
- `rgb2cmap`: chooses the nearest 8-bit color-map entry by Euclidean RGB distance.
- `cmap2rgb`: decodes Plan 9 CMAP8 indices into 24-bit RGB.
- `cmap2rgba`: extends `cmap2rgb` with opaque alpha.

Important behavior:
- The original direct inverse mapping is retained in comments but replaced by slower nearest-color search for better visual output on arbitrary RGB triples.
