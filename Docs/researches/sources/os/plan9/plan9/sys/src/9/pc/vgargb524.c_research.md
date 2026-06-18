# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgargb524.c

IBM RGB524 RAMDAC hardware cursor support, assuming an S3 Vision964/968-style connection. The file defines indirect index/data register access through standard DAC ports selected by CRTC register `0x55`.

Cursor behavior:
- `rgb524setrs2()` selects the RS2 address bank and returns prior CRTC state.
- `rgb524xo()` writes indexed RGB524 registers.
- `rgb524enable()` disables cursor, sets cursor color 1 white and color 2 black, then enables 32x32 mode 2.
- `rgb524disable()` clears `CursorCtl`.
- `rgb524load()` sets auto-increment addressing, writes the 32x32 cursor array as packed two-plane pixels, programs hotpoint registers from negative cursor offsets, enables cursor, and restores CRTC state.
- `rgb524move()` writes cursor X/Y low/high registers.

Exports `VGAcur vgargb524cur` only.
