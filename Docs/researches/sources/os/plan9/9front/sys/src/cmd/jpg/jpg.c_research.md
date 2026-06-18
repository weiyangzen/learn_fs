# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/jpg.c

This is the JPEG viewer/converter frontend.

Key behavior:
- Reads JPEG via `Breadjpg()` into YCbCr or RGB depending on flags and display depth.
- Supports display, compressed raw output, Plan 9 uncompressed output, greyscale, RGB24, RGBV, no-dither, and decode-only modes.
- Supports field merging for interlaced/video JPEG pairs with `-f` and movie mode with `-F`.
- Converts `Rawimage` to display/output channel formats using `torgbv()` or `totruecolor()`.
- Handles repeated frames in movie mode by looping back to decode more JPEGs from the stream.

Research notes:
- `vidmerge()` interleaves scanlines from two decoded images and validates dimensions/channel metadata.
