# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/readpng.c

PNG reader backed by Plan 9 `flate` zlib inflation and CRC checking. It verifies the PNG signature, reads chunks through `getchunk`, requires IHDR, accepts PLTE while streaming, and decompresses IDAT data through callback-based inflate.

It supports PNG color types 0, 2, 3, 4, and 6 with bit depths allowed by the format checks, converts indexed pixels through the palette, handles alpha into `CYA16`/`CRGBA32`, and supports Adam7 interlacing. Scanline filters include None, Sub, Up, Average, and Paeth.

The decoder emits one-channel packed true-color style `Rawimage` buffers (`CY`, `CRGB24`, `CYA16`, `CRGBA32`). Many parse failures call `sysfatal`, so callers do not receive recoverable errors for malformed PNGs.
