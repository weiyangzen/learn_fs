# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/wrbmp.c

IJG `djpeg` output module for Microsoft BMP in Windows 3.x and OS/2 1.x formats. It supports uncompressed 8-bit colormapped/grayscale and 24-bit RGB output.

Main data structures and entry points:
- `bmp_dest_struct` extends `djpeg_dest_struct` with OS/2 mode, virtual whole-image buffer, row widths, padding count, and current output row.
- `jinit_write_bmp` validates colorspace, calculates output dimensions, computes 4-byte BMP row padding, requests a virtual array, and allocates one decompressor row buffer.
- `start_output_bmp` is intentionally empty because headers are emitted in `finish_output_bmp` after the full image is buffered.
- `finish_output_bmp` writes the selected header/colormap, then writes virtual rows bottom-to-top.

Output routines:
- `put_pixel_rows` stores 24-bit rows in BGR order and zeroes row padding.
- `put_gray_rows` stores grayscale or palette index rows and zeroes padding.
- `write_bmp_header` emits BITMAPFILEHEADER + Windows BITMAPINFOHEADER and optional BGR0 colormap.
- `write_os2_header` emits BITMAPFILEHEADER + OS/2 BITMAPCOREHEADER and optional BGR colormap.
- `write_colormap` writes RGB colormap, grayscale colormap, or a generated linear grayscale map.

Important constraints:
- 12-bit `JSAMPLE` builds are rejected by deliberate compile-time syntax error.
- Full image buffering is required to invert JPEG top-down row order into BMP bottom-up row order.
- BMP rows are padded to 4-byte boundaries.

Filesystem relevance:
- Sequential output writer with a virtual memory-backed image reorder pass; no filesystem internals.
