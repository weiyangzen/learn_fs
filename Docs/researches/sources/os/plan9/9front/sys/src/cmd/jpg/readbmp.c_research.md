# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/readbmp.c

BMP decoder for the Plan 9 image tools. It reads MS BMP and limited OS/2 1.x BMP headers, handles little-endian header fields, optional color tables/bitfields, and returns `Rawimage**` through `Breadbmp`/`readbmp`.

It supports 1, 4, 8, 16, 24, and 32 bpp input, including RLE4/RLE8 and bottom-up or top-down orientation. Indexed formats expand through a CLUT; true-color formats are split into three `CRGB` channels.

Errors are a mix of `sysfatal`, `werrstr`, and `nil` returns. Image dimensions and allocation sizes are trusted after header parsing, so this is format-decoding utility code rather than hardened untrusted-input infrastructure.
