# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsgi.c

Purpose: Ghostscript printer-style output device that writes SGI RGB raster image files.

Key behavior:
- Defines `sgirgb`, a 24-bit RGB printer device at 72 dpi.
- Implements RGB color index packing/unpacking according to device depth.
- Writes an SGI image header with magic `IMAGIC`, RLE type, dimensions, 3 channels, and normal colormap.
- Reserves row-start and row-size tables, then emits channel-separated RLE data bottom-up.
- Encodes each R/G/B separation independently with SGI-style RLE packets and later seeks back to fill the offset/size tables in big-endian byte order.

Important dependencies:
- Ghostscript printer API and SGI image definitions from `gdevsgi.h`.

Notable risks / findings:
- Allocation failure paths can return without freeing allocations already made in `sgi_begin_page`.
- Uses `bzero` and manual `fseek`/`fwrite` table patching typical of older C code.
