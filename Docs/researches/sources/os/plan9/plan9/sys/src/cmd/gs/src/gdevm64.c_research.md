# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm64.c

Implements 64-bit memory devices `image64` and little-endian `image64w`. Pixels are represented as two 32-bit chunks after endian-aware unpacking.

`mem_true64_fill_rectangle` fills direct 64-bit pixels using repeated pairs of 32-bit stores. Unlike 40/48/56-bit files, there is no rotated byte cache because the pixel size aligns cleanly to 8 bytes.

`mem_true64_copy_mono` supports opaque and stencil mono copies by writing two-word pixels for set or unset source bits. `mem_true64_copy_color` delegates to `mem_copy_byte_rect`.

The word-oriented variant swaps 64-bit pixel bit ranges before/after standard operations and copies color bytes with `bytes_copy_rectangle`.

This is the simplest high-depth backend structurally because the stride is word-aligned, though it still uses endian-specific color unpacking.
