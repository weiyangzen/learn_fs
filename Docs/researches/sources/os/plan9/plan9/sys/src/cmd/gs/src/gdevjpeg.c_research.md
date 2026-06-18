# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevjpeg.c

JPEG output driver built on Ghostscript’s DCT/JPEG stream wrappers and IJG library.

Key behavior:
- Defines `jpeg` RGB, `jpeggray`, and `jpegcmyk` devices.
- Exposes `JPEGQ` and `QFactor`; `JPEGQ` takes precedence.
- CMYK path stores inverted CMYK values for compatibility with Photoshop-style CMYK JPEG expectations.
- `jpeg_print_page` creates JPEG compression state, sets image size/color space/density, applies quality, streams each scanline into a DCTEncode filter, and flushes to output file.

Risks / notes:
- No alpha/deviceN support; only 8-bit gray, 24-bit RGB, and 32-bit CMYK.
- Quality parameter validation is simple and delegated to JPEG setup routines.
