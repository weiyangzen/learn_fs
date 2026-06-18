# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/bmp.c

This is the BMP viewer/converter frontend for the Plan 9 image tools.

Key behavior:
- Reads BMP via `readbmp(fd, CRGB)`.
- Displays images using libdraw/event unless `-d` or output flags suppress display.
- Converts decoded `Rawimage` to CMAP8, GREY8, or RGB24 via `torgbv()` / `totruecolor()`.
- Can write Plan 9 uncompressed image format with `-9` or compressed raw image with `-c`.
- Supports color/dither options shared with other image frontends.

Research notes:
- Output modes exit after one file when multiple inputs are given.
- The display path centers the image and waits for one keyboard event.
