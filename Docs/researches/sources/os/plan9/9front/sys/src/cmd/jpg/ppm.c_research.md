# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/ppm.c

This is the PPM/pixmap viewer/converter frontend.

Key behavior:
- Reads pixmap data via `readpixmap(fd, CRGB)`.
- Supports the common frontend flags for display suppression, raw output, Plan 9 image output, dithering, greyscale, RGB24, RGBV, and three-color output.
- Converts to CMAP8 with `torgbv()` or to true-color/greyscale with `totruecolor()`.
- Displays centered image and waits for a keyboard event.
- Writes either raw compressed image or Plan 9 uncompressed image header plus pixel data.

Research notes:
- Closely mirrors `bmp.c`, with format-specific decode and command names changed.
