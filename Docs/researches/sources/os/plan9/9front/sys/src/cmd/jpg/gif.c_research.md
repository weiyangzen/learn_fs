# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/gif.c

This is the GIF viewer/converter frontend.

Key behavior:
- Reads GIF frames via `readgif(fd, CRGB, dflag)`.
- Handles animated GIFs, frame delays, loop counts, disposal modes, and transparency masks.
- Displays animation with libdraw/event unless suppressed.
- Converts output to CMAP8, GREY8, RGB24, or alpha-bearing formats when transparency is present.
- Writes Plan 9 image or compressed raw image output for the first frame.

Research notes:
- `addalpha()` and `blackout()` convert GIF transparency into alpha channels for output formats.
- Uses a global `allims`/`which` pair for resize redraw of the current animation frame.
