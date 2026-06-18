# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm56.c

Implements 56-bit memory devices `image56` and little-endian `image56w`. Pixels are seven bytes, requiring a seven-word rotated cache for efficient wide fills.

`mem_true56_fill_rectangle` handles gray colors via `memset`, non-gray wide fills via cached 32-bit word rotations, and narrow widths with direct byte assignments. The fill loops are stride-specialized for 7-byte pixels.

`mem_true56_copy_mono` writes unpacked 7-byte colors for opaque and stencil mono copies. It processes first partial source byte, full bytes, and final residual bits similarly to the 24/40/48-bit devices.

`mem_true56_copy_color` delegates to byte rectangle copying. The word-oriented device swaps affected bit ranges around standard operations.

The file is largely generated-pattern-like relative to the other high-depth memory devices, but the 7-byte stride makes cache and alignment cases especially error-prone.
