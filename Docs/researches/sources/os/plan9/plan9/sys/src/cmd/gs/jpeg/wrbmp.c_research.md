# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrbmp.c

IJG `djpeg` destination adapter for uncompressed BMP output, compiled only under `BMP_SUPPORTED`.

Responsibilities:

- Supports Microsoft Windows 3.x BMP and OS/2 1.x BMP headers.
- Emits either 24-bit BGR rows or 8-bit indexed/grayscale rows with colormaps.
- Requires 8-bit `JSAMPLE`; 12-bit JPEG output is intentionally unsupported.
- Uses a full-image virtual array because BMP stores rows bottom-up while JPEG decompression supplies rows top-down.

Key functions:

- `put_pixel_rows()` converts RGB to BGR and appends row padding.
- `put_gray_rows()` stores grayscale or palette-index rows with padding.
- `write_bmp_header()` and `write_os2_header()` generate file/info headers and choose colormap sizes.
- `write_colormap()` emits BGR0 Windows map entries or BGR OS/2 entries, synthesizing a grayscale ramp when needed.
- `finish_output_bmp()` writes the header and then flushes the virtual image from bottom to top.
- `jinit_write_bmp()` validates output color space, calculates padded row width, allocates the virtual array and row buffer, and installs callbacks.

The module is a format writer behind `djpeg`; all persistent storage interaction is ordinary stdio output.
