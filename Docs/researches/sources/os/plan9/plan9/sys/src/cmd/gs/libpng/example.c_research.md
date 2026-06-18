# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/example.c

Non-compiling libpng instructional example, disabled by top-level `#if 0`.

Purpose:

- Demonstrates how applications can read and write PNG files with libpng.
- Explicitly says missing application-specific pieces must be supplied and points to `pngtest.c` for a minimal working program.

Covered read patterns:

- `check_if_png()` opens a file, reads four signature bytes, and checks them with `png_sig_cmp()`.
- Two `read_png()` prototypes show filename-owned and already-open-file flows.
- Demonstrates `png_create_read_struct()`, `png_create_info_struct()`, `setjmp` error handling, standard I/O via `png_init_io()` or custom read callbacks, `png_set_sig_bytes()`, `png_read_info()`, `png_get_IHDR()`, and high-level `png_read_png()`.
- Shows optional transforms: strip 16-bit, strip alpha, packing, palette-to-RGB, grayscale expansion, tRNS-to-alpha, background compositing, gamma correction, dithering, monochrome inversion, sBIT shifting, BGR ordering, alpha swapping, endian swapping, filler bytes, and interlace handling.
- Demonstrates whole-image and row-by-row reads, followed by `png_read_end()` and `png_destroy_read_struct()`.

Progressive read examples:

- `initialize_png_reader()` creates read/info structs, sets setjmp handling, and installs progressive callbacks.
- `process_data()` feeds byte chunks into `png_process_data()`.
- `info_callback()`, `row_callback()`, and `end_callback()` show where to prepare transforms, combine rows with `png_progressive_combine_row()`, and mark completion.

Write pattern:

- `write_png()` demonstrates `png_create_write_struct()`, `png_create_info_struct()`, `png_init_io()` or custom write callbacks, high-level `png_write_png()`, lower-level `png_set_IHDR()`, palette setup, sBIT/gAMA/text metadata, transform setup, interlace handling, `png_write_image()` or `png_write_rows()`, `png_write_end()`, explicit freeing of caller-allocated palette/auxiliary data, and `png_destroy_write_struct()`.

This file is documentation-as-code and is intentionally excluded from compilation.
