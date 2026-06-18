# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/onechan.c

This helper converts images to one byte per pixel, usually CMAP8/RGBV or greyscale.

Key behavior:
- Leaves GREY and CMAP8 images unchanged.
- Fast-paths RGB16, RGB24, RGBA32, and ARGB32 by unpacking into temporary RGB channels.
- Uses `torgbv()` to quantize RGB into Plan 9 colormap indices.
- Converts other image channels by first drawing to RGB24.
- Provides both `Image` and `Memimage` versions.

Research notes:
- Temporary `Rawimage` channel buffers are manually allocated and freed around the `torgbv()` call.
