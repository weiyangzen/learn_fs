# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgabt485.c

Hardware cursor support for Brooktree Bt485 RAMDAC, assuming an S3 86C928-style connection. The file defines indirect DAC register offsets, DAC register-address selection through CRTC register `0x55`, and helper accessors `bt485i()`/`bt485o()`.

Cursor behavior:
- `bt485enable()` disables the cursor, sets overscan and cursor colors, and enables S3/Bt485 external cursor operation through CRTC registers `0x55` and `0x45`.
- `bt485disable()` clears DAC cursor mode and S3 cursor control bits.
- `bt485load()` writes a 64x64 two-plane cursor RAM image, stores hotpoint offset as `64 + curs->offset`, and enables cursor mode.
- `bt485move()` writes cursor X/Y low/high DAC registers.

Exports only `VGAcur vgabt485cur` named `"bt485hwgc"`. The header notes 64x64x2 cursor is always used and interlaced mode is unsupported.
