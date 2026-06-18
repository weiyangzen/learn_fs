# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/example.c

Public-domain libpng example file, wrapped in `#if 0`, intended as instructional pseudo-code rather than directly compilable source.

Read-side coverage:
- `check_if_png` demonstrates opening a file, reading signature bytes, and using `png_sig_cmp`.
- `read_png` shows two prototypes: one opening by filename and one accepting an already-open `FILE *` plus `sig_read`.
- Demonstrates `png_create_read_struct`, `png_create_info_struct`, `setjmp(png_jmpbuf(...))`, `png_init_io` or `png_set_read_fn`, `png_set_sig_bytes`, `png_read_info`, and `png_get_IHDR`.
- Shows common transforms: strip 16-bit, strip alpha, packing, palette/grayscale expansion, tRNS alpha, background composition, gamma/sRGB, dithering, invert mono, sBIT shift, BGR swap, alpha swap, byte swap, filler, and interlace handling.
- Shows full-image, row-at-a-time, multi-row, and progressive display read patterns, ending with `png_read_end` and `png_destroy_read_struct`.

Progressive read coverage:
- `initialize_png_reader` demonstrates progressive callbacks via `png_set_progressive_read_fn`.
- `process_data` feeds incoming bytes into `png_process_data`.
- `info_callback`, `row_callback`, and `end_callback` document setup timing, row combination via `png_progressive_combine_row`, and completion handling.

Write-side coverage:
- `write_png` demonstrates `png_create_write_struct`, `png_create_info_struct`, setjmp error cleanup, `png_init_io` or `png_set_write_fn`, `png_set_IHDR`, `png_set_PLTE`, optional chunks/text/gamma/sBIT, `png_write_info`, write transforms, interlace handling, `png_write_image` or `png_write_rows`, `png_write_end`, freeing user-allocated data, and `png_destroy_write_struct`.

Important caveat:
- The file intentionally contains placeholders (`ERROR`, `OK`, undefined variables, `PNG_COLOR_TYPE_???`) and is disabled from compilation.

Filesystem relevance:
- Documentation/example for PNG file IO through libpng; no filesystem implementation logic.
