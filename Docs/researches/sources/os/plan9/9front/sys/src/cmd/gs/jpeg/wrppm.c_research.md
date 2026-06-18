# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/wrppm.c

IJG `djpeg` output module for raw PPM/PGM images, compiled when `PPM_SUPPORTED` is enabled.

Main data structures and entry points:
- `ppm_dest_struct` extends `djpeg_dest_struct` with physical IO buffer, optional decompressor row alias, byte width, and sample count.
- `jinit_write_ppm` allocates the destination, computes dimensions, allocates the physical IO buffer, and selects a row writer based on quantization and sample representation.
- `start_output_ppm` emits `P5` for grayscale or `P6` for RGB with width, height, and `PPM_MAXVAL`.
- `finish_output_ppm` flushes and checks write errors.

Row writers:
- `put_pixel_rows` directly writes the decompressor row for the normal 8-bit case.
- `copy_pixel_rows` translates sample width, mainly for 12-bit mode.
- `put_demapped_rgb` and `put_demapped_gray` expand quantized color-map indexes to RGB or grayscale sample bytes/words.

Important behavior:
- `PUTPPMSAMPLE`, `BYTESPERSAMPLE`, and `PPM_MAXVAL` adapt output for 8-bit, downscaled 12-bit, or nonstandard raw word-per-sample PPM/PGM.
- Direct-write mode maps `pub.buffer` onto `iobuffer` to avoid copying.
- Unsupported output colorspaces fail with `JERR_PPM_COLORSPACE`.

Filesystem relevance:
- Sequential image writer using stdio; no filesystem semantics.
