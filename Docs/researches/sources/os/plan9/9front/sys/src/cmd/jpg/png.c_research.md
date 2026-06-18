# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/png.c

This is the PNG viewer/converter frontend.

Key behavior:
- Reads PNG via `Breadpng(&b, CRGB)`.
- Supports display, compressed raw output, Plan 9 uncompressed output, debug flag, greyscale/RGB24/RGBV/CMAP8 modes, and dither control.
- Preserves PNG-decoded channel descriptors such as GREY+alpha and RGBA when writing/displaying true-color output.
- Uses a black background composition image for display so alpha effects are visible.
- Frees raw channel buffers after processing.

Research notes:
- Usage string mentions `-r`, but option parsing does not implement `r`.
