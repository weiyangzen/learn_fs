# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbmp.c

Ghostscript synchronous BMP file output devices.

Key behavior:
- Defines BMP devices:
  - `bmpmono`: 1-bit monochrome.
  - `bmpgray`: 8-bit grayscale with fixed 256-gray palette.
  - `bmpsep1`: separated CMYK, 1 bit per plane.
  - `bmpsep8`: separated CMYK, 8 bits per plane.
  - `bmp16`: 4-bit EGA/VGA-style color.
  - `bmp256`: 8-bit 3-3-2 palette color.
  - `bmp16m`: 24-bit color using BGR byte order.
  - `bmp32b`: 32-bit CMYK-like output outside the BMP specification.
- `bmp_print_page` writes a BMP header, then writes rows bottom-to-top with 32-bit row padding.
- `bmp_cmyk_print_page` writes four separate BMP images, one per CMYK plane, each bottom-to-top, using render-plane extraction.

Notable dependencies:
- Ghostscript printer APIs: `gdevprn.h`.
- PC color mapping helpers: `gdevpccm.h`.
- Shared BMP helpers from `gdevbmp.h` / `gdevbmpc.c`.

Research notes:
- Multi-plane separated CMYK output concatenates multiple BMP image streams into one output file; many ordinary BMP readers will only display the first.
- The synchronous path allocates only one padded row buffer and streams output directly.
- BMP row padding bytes are zeroed once after allocation; the image copy fills only active raster bytes for each row.
