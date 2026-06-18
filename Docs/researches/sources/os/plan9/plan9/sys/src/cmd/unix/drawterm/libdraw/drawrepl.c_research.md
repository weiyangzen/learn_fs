# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/drawrepl.c

Implements coordinate wrapping for replicated images.

Key functions:
- `drawreplxy`: maps a coordinate into `[min, max)` using modulo arithmetic corrected for negative inputs.
- `drawrepl`: applies `drawreplxy` to both axes of a `Point` within a `Rectangle`.

Used by clipping, repeated image reads, and raster operations that need source or mask tiling.
