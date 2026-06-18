# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtfnx.c

## Purpose
Implements uncompressed RGB TIFF output devices `tiff12nc` and `tiff24nc`.

## Main Concepts
- Defines a simple `gx_device_tiff` printer wrapper with `gdev_tiff_state`.
- Registers 24-bit RGB printer devices for both output modes.
- Uses TIFF tags for RGB photometric interpretation, no compression, MSB fill order, and three samples per pixel.
- `tiff12nc` stores three 4-bit RGB samples packed into 12 bits per pixel; `tiff24nc` stores 8-bit RGB samples.

## Key Functions
- `tiff12_print_page`: writes a TIFF directory using 4/4/4 bits per sample, converts 24-bit RGB scanlines into packed 12-bit RGB data, and emits rows.
- `tiff24_print_page`: writes a TIFF directory using 8/8/8 bits per sample and copies RGB scanlines directly.

## Dependencies
Uses Ghostscript printer APIs and the shared TIFF writer declarations in `gdevtifs.h`.

## Notable Risks
- If line allocation fails after `gdev_tiff_begin_page`, the page directory has already been written and is not closed/patched.
- `tiff12_print_page` loops over `raster` in 6-byte input chunks, which relies on the 24-bit scanline layout matching that conversion.
- Write errors are not checked.

## Filesystem Relevance
Writes TIFF image streams. It is not filesystem implementation code.
