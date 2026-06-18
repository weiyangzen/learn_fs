# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/draw.c

VNC client-side framebuffer update decoder and screen updater.

Key responsibilities:
- Sends the requested RFB encoding list.
- Sends framebuffer update requests sized to the local screen and server dimensions.
- Decodes server rectangles for raw, copyrect, RRE, CoRRE, hextile, and mouse-warp encodings.
- Converts incoming pixels through `cvtpixels` when negotiated by `color.c`.
- Loads decoded pixel data into Plan 9 draw images and draws onto the display.
- Handles server messages: framebuffer update, colormap, bell, server ack, and server cut text.

Important behavior:
- `pixbuf` stores a full rectangle in local screen pixel size; `linebuf` supports converted row input.
- Rectangles are clipped when local screen size is smaller than server size.
- Hextile maintains tile-local background/foreground colors.
- After each framebuffer update, it flushes the display and requests an incremental update.

Risks:
- Bad server geometry or encoding is fatal.
- Pixel buffers are allocated for full server dimensions and kept globally.
