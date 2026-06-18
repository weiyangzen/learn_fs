# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/color.c

Pixel-format negotiation and local color conversion for the VNC client path.

Key responsibilities:
- Converts Plan 9 draw channel descriptors into RFB `Pixfmt` masks and shifts.
- Chooses a VNC pixel format matching the local screen.
- Handles 24-bit local screens by requesting 32 bpp and dropping the padding byte.
- Emulates 8-bit `CMAP8` either through 12-bit RGB or compact BGR332 input, converting back to Plan 9 cmap indexes.
- Sends the negotiated pixel format to the server.

Important behavior:
- VNC is kept little-endian.
- Conversion callback `cvtpixels` is set globally for later rectangle decoding.
- Unsupported screen channels or non-byte-aligned depths are fatal.

Risks:
- CMAP conversions are lossy.
- Global conversion state assumes one active VNC display path.
