# File Research: sources/os/plan9/plan9/sys/src/cmd/page/rotate.c

Provides image rotation and resampling routines for `page`. `rot180` uses a logarithmic draw-mask shuffle algorithm to reverse X and Y axes with an auxiliary image, optimizing for remote draw performance. Sub-byte images are temporarily converted to `CMAP8`.

`rot90` and `rot270` allocate transposed images and copy pixels one at a time through draw operations, then free the source image.

The resampler uses a Kaiser-windowed filter table and performs two-pass resizing: first X into scanline buffers, then Y into destination scanlines. It supports byte-per-channel formats directly and converts palette/sub-byte formats through `RGB24` or `GREY8` temporary images.

Allocation failures in transform paths are fatal via `wexits`/`sysfatal`; unsupported channel types also abort.
