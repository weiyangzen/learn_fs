# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/wrtarga.c

IJG `djpeg` output module for Targa/TGA images, compiled when `TARGA_SUPPORTED` is enabled.

Main data structures and entry points:
- `tga_dest_struct` extends `djpeg_dest_struct` with a physical row buffer and row width.
- `jinit_write_targa` computes output dimensions, allocates an IO row buffer, and allocates a decompressor row buffer.
- `start_output_tga` validates output colorspace, writes a TGA header, optionally writes an RGB colormap, and selects row writer.
- `finish_output_tga` flushes and checks write errors.

Output routines:
- `write_header` emits an 18-byte top-down noninterlaced TGA header for grayscale, colormapped RGB, or truecolor RGB.
- `put_pixel_rows` writes unquantized RGB rows in BGR byte order.
- `put_gray_rows` writes grayscale rows or quantized palette indexes.
- `put_demapped_gray` expands quantized grayscale through the colormap because TGA lacks mapped grayscale.

Important constraints:
- Only 8-bit `JSAMPLE` builds are supported.
- RGB colormaps are limited to 256 colors and are written in BGR order.
- The writer emits top-down TGA (`descriptor` bit 5 set), avoiding whole-image row inversion.

Filesystem relevance:
- Sequential image-output module; no filesystem behavior.
