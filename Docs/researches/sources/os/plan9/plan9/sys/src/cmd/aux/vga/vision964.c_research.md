# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vision964.c

S3 Vision964 controller support.

Key behavior:
- Snarfs generic S3 state plus CRTC registers `0x22`, `0x24`, and `0x26`.
- Advertises linear and enhanced mode.
- Rejects depths above 8 bpp.
- If RAMDAC uses clock doubling, halves horizontal timings and forces enhanced mode; otherwise enhanced mode is used for 8 bpp.
- Configures external SID width/divisor based on RAMDAC flags `Hsid32` and `Uclk2`.
- Sets SAM size, display FIFO start, enhanced control bits, delay/skew attributes, and optional `sam512`.
- Loads `Crt65`, `Crt66`, `Crt6D`, and advanced-function control.

Filesystem relevance:
- Indirect display controller support.
