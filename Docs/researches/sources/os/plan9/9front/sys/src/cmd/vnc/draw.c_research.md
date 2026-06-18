# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/draw.c

## Role

`draw.c` is the VNC viewer's framebuffer update decoder and local screen updater. It sends preferred encodings and framebuffer update requests, then decodes server-to-client rectangle updates into the Plan 9 draw window.

## Encoding Negotiation And Requests

- `sendencodings()` parses the `encodings` string and sends `MSetEnc`.
- Supported names include raw, copyrect, RRE, CoRRE, hextile, mousewarp, desktopsize, and xdesktopsize.
- `requestupdate()` flushes the local display, optionally sends extended desktop resize state, and requests full or incremental updates.

## Update Decoding

- Maintains decompression buffers `pixbuf` and `linebuf`.
- Handles raw pixel rectangles, copyrect, RRE, CoRRE, hextile, cursor/mouse warp, and desktop-size pseudo-encodings.
- `loadbuf()` reads pixel data, applies conversion through `cvtpixels` if needed, and optionally scales pixels for autoscale mode.
- `updatescreen()` clips to local display size and uses `loadimage()` into the Plan 9 screen.
- `dohextile()` decodes hextile tiles with background, foreground, subrect, and colored-subrect flags.
- Clipboard messages delegate to `writesnarf()`.

## Notable Limitations And Risk Areas

- Bad rectangles or unknown encodings are fatal.
- Autoscale uses simple nearest-neighbor style in-buffer scaling and depends on current screen/window dimensions.
- Pixel buffer sizing follows the remote framebuffer dimensions; large remote screens can allocate large buffers.
- Some resize paths depend on server support for desktop-size pseudo-encodings.
