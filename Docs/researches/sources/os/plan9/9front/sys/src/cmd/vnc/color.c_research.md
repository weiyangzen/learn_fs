# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/color.c

## Role

`color.c` chooses the viewer-side pixel format advertised to the VNC server and installs conversion functions when the local Plan 9 display format is not directly usable over RFB.

## Main Behavior

- Converts Plan 9 draw channel descriptors into VNC `Pixfmt` fields.
- Supports 24-bit local screens by requesting 32 bpp from the server and dropping the unused byte.
- Supports CMAP8 displays in two emulation modes:
  - 12-bit RGB packed into 16 bpp with `RGB12` and a lookup table to CMAP8.
  - 8-bit BGR332 with a lookup table to CMAP8.
- Sets `cvtpixels` when a per-pixel conversion is needed.
- Sends an `MPixFmt` message to the server after selecting the format.

## Notable Limitations And Risk Areas

- Only byte-aligned local depths are accepted.
- Failure to discover red, green, and blue channels is fatal.
- CMAP conversion intentionally loses precision in the BGR332 path.
- Conversion is designed for little-endian VNC pixel streams.
