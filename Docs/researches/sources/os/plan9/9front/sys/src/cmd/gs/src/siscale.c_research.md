# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/siscale.c

Implements smoothed image scaling streams using a Mitchell filter.

Key points:
- Based on public domain Graphics Gems III scaling code.
- Supports fixed-point accumulation when no FPU is configured and floating-point accumulation otherwise.
- Defines contribution list structures for precomputed horizontal and vertical filter weights.
- `calculate_contrib` computes clamped/wrapped contributor ranges and weights for each output sample, including squeeze handling for downscaling.
- `zoom_x` horizontally filters source rows into an intermediate `PixelTmp` ring buffer.
- `zoom_y` vertically filters intermediate rows into final output rows, clamping to the output maximum.
- Stream initialization allocates source, destination, intermediate, contribution, and weight buffers, calculates X contributions, and prepares the first Y contribution.
- Processing reads complete source rows, horizontally filters them, emits vertically filtered output rows when enough source support is available, and buffers partial output rows as needed.
- Release frees all allocated buffers.

Dependencies and interactions:
- Uses `sisparam.h` through `siscale.h`.
- Uses `gconfigv.h` `USE_FPU` and Ghostscript stream/memory APIs.

Research relevance:
- This is Ghostscript's higher-quality separable image resizing filter implementation.
