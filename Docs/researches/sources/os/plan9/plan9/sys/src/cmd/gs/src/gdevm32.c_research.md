# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm32.c

Implements 32-bit memory devices `image32` and little-endian `image32w`. The device reports 24 color bits plus 8 alpha/extra bits and uses default RGB/CMYK mapping.

`mem_true32_fill_rectangle` arranges color bytes for host endian order, then fills 32-bit pixels. It has specialized paths for widths 1 to 4, zero-color `memset`, and wider repeated 32-bit stores.

`mem_true32_copy_mono` has an optimized transparent-zero case for character masks, writing only one-colored set bits. The opaque path writes zero/one colors per source bit, respecting transparent `one`.

`mem_true32_copy_color` delegates to `mem_copy_byte_rect`. The word-oriented variant swaps colors for fill/copy-mono and byte-swaps copied color rectangles.

The file is simpler than 24-bit because 32-bit pixels align naturally to word boundaries, reducing pattern-rotation complexity.
