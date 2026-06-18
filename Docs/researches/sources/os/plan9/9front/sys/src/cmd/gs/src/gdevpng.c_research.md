# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpng.c

Ghostscript PNG output devices backed by libpng. It provides monochrome, indexed-color, grayscale, RGB, high-depth RGB, and RGBA-with-coverage devices, all using the generic printer framework.

Key behavior:
- Defines `pngmono`, `png16`, `png256`, `pnggray`, `png16m`, and `png48` printer devices with appropriate color mapping and depths.
- Defines a special `pngalpha` 32-bit RGBA printer device whose alpha channel represents pixel coverage rather than general transparency.
- `png_print_page` is shared by all PNG devices. It allocates one raster row, creates libpng write/info structs, sets resolution metadata, selects PNG color type/bit depth from Ghostscript device depth, writes palette metadata when needed, emits a `Software` text chunk, streams rendered scanlines through `png_write_rows`, then finalizes the PNG.
- For 32-bit alpha output, it uses `PNG_COLOR_TYPE_RGB_ALPHA`, inverts alpha for libpng output, and writes a `bKGD` chunk from `BackgroundColor`.
- For 48-bit RGB output, it conditionally byte-swaps on little-endian hosts.
- `pngalpha_open` installs a custom buffer-device creator and intercepts `fill_rectangle` after opening so full-page white erase becomes transparent.
- `pngalpha_create_buf_device` restores alpha-copy behavior into memory buffers created under the printer framework.
- `pngalpha_get_params` and `pngalpha_put_params` expose `BackgroundColor`.
- `pngalpha_encode_color` and `pngalpha_decode_color` use `0xRRGGBB00` opaque pixels, reserving the low byte as inverted alpha/coverage.
- `pngalpha_fill_rectangle` maps whole-page white fill to nearly transparent coverage.
- `pngalpha_copy_alpha` implements slow but functional coverage compositing for depth 2/4 alpha masks by reading existing pixels, blending RGB and coverage, and writing accumulated lines back.

Notable dependencies:
- Ghostscript printer/memory/palette/version APIs: `gdevprn.h`, `gdevmem.h`, `gdevpccm.h`, `gscdefs.h`.
- libpng through `png_.h`, with `PNG_NO_CONSOLE_IO` and compatibility stubs for progressive-read builds.

Research notes:
- The file directly manipulates older libpng struct fields such as `info_ptr->width`, reflecting the vendored Ghostscript era.
- If `png_create_write_struct` fails, `png_create_info_struct(png_ptr)` is still called before the null check; with libpng APIs that require a non-null write struct, that ordering is fragile.
- The palette allocation is freed explicitly after `png_write_end`, but if an error jumps to `done` after palette allocation, cleanup depends on `info_ptr->palette` still being safe for `gs_free_object`.
