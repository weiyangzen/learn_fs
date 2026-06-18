# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/png.h

## Role

`png.h` is the main libpng 1.2.8 header bundled under Plan 9 Ghostscript’s `libpng` directory. It is not filesystem code; it is third-party image codec API and internal declaration surface used by Ghostscript’s PNG support.

The file combines public API declarations, public data structures, compile-time feature gates, and, when `PNG_INTERNAL` is defined, private libpng declarations used by the implementation `.c` files.

## Version And Build Identity

The header identifies libpng version `1.2.8`, dated December 3, 2004. Important version macros include:

- `PNG_LIBPNG_VER_STRING "1.2.8"`
- `PNG_HEADER_VERSION_STRING`
- `PNG_LIBPNG_VER_MAJOR 1`
- `PNG_LIBPNG_VER_MINOR 2`
- `PNG_LIBPNG_VER_RELEASE 8`
- `PNG_LIBPNG_VER 10208`
- `PNG_LIBPNG_VER_DLLNUM 13`

The top of the file contains a long compatibility history for libpng version numbers and shared-library numbering. This matters because later code exposes `png_access_version_number()`, `png_get_header_ver()`, `png_get_libpng_ver()`, and uses a typedef `version_1_2_8` to catch mismatches between `png.c` and `png.h`.

## Dependencies

`png.h` includes `zlib.h` unless `PNG_VERSION_INFO_ONLY` is defined, then includes `pngconf.h`. Almost every type, export macro, calling convention, optional feature macro, and portability typedef visible in this file comes from `pngconf.h`.

The header has `extern "C"` guards for C++ consumers.

## Public Data Types

The file defines the canonical libpng public types:

- `png_color`: 8-bit RGB palette entry.
- `png_color_16`: 16-bit/indexed color container used for transparency and background.
- `png_color_8`: significant-bit information per channel.
- `png_sPLT_entry` and `png_sPLT_t`: suggested palette chunk storage.
- `png_text`: text/zTXt/iTXt metadata, conditional on text support.
- `png_time`: PNG tIME chunk representation.
- `png_unknown_chunk`: private/unknown chunk retention structure.
- `png_info`: image metadata and optional ancillary chunk state.
- `png_row_info`: row transformation metadata.
- `png_struct`: opaque public handle typedef, with the actual `struct png_struct_def` exposed in this older libpng header.

The `png_info` structure records IHDR metadata, valid-chunk bit flags, palette, row byte count, optional chunk state, text, transparency, gamma/chromaticity, physical dimensions, ICC/sPLT/sCAL data, unknown chunks, and optionally full image row pointers.

The exposed `png_struct_def` is large and carries runtime state: error/warning callbacks, I/O callbacks, transform callbacks, zlib stream and compression settings, image dimensions, row buffers, CRC/chunk state, palette/transparency state, gamma tables, progressive-read buffers, dithering/filter state, optional user memory callbacks, MNG feature flags, assembler/MMX flags, and user width/height limits.

Because this old libpng version exposes struct layouts, binary compatibility depends on the exact feature macros used when building both the library and application.

## Constants And Flags

The header defines PNG format constants and libpng state flags, including:

- Color types: grayscale, palette, RGB, RGB+alpha, grayscale+alpha.
- Compression/filter/interlace constants.
- Ancillary chunk validity flags such as `PNG_INFO_gAMA`, `PNG_INFO_PLTE`, `PNG_INFO_tRNS`, `PNG_INFO_iCCP`, `PNG_INFO_sPLT`, `PNG_INFO_IDAT`.
- Transform masks such as `PNG_TRANSFORM_STRIP_16`, `PNG_TRANSFORM_EXPAND`, `PNG_TRANSFORM_BGR`, `PNG_TRANSFORM_SWAP_ENDIAN`.
- CRC handling modes for `png_set_crc_action()`.
- Filter constants and filter heuristic constants.
- Memory-free ownership flags such as `PNG_FREE_TEXT`, `PNG_FREE_PLTE`, `PNG_FREE_ALL`.
- Unknown chunk handling modes.
- Internal mode and transformation flags under `PNG_INTERNAL`.
- Internal row sizing macro `PNG_ROWBYTES(pixel_bits, width)`.

Chunk type names are defined as byte arrays under `PNG_INTERNAL`, including `IHDR`, `IDAT`, `IEND`, `PLTE`, `bKGD`, `cHRM`, `gAMA`, `iCCP`, `iTXt`, `pHYs`, `sRGB`, `tEXt`, `tIME`, `tRNS`, and `zTXt`.

## Public API Surface

The file declares the main libpng API families:

- Version and signature checks: `png_access_version_number()`, `png_sig_cmp()`, `png_check_sig()`.
- Object creation/destruction: `png_create_read_struct()`, `png_create_write_struct()`, `png_create_info_struct()`, destroy functions.
- Read/write setup: `png_init_io()`, `png_set_read_fn()`, `png_set_write_fn()`.
- Error handling: `png_set_error_fn()`, `png_get_error_ptr()`, `png_error()`, `png_warning()`, chunk-prefixed variants.
- Compression and filtering control: `png_set_filter()`, zlib level/method/window/memory/strategy setters.
- Transform setup: expand, BGR, gray/RGB conversion, strip alpha/16-bit, swap bytes, packing, gamma, background, filler, interlace handling, dithering.
- Sequential reading/writing: `png_read_info()`, `png_read_row(s)`, `png_read_image()`, `png_read_end()`, `png_write_info()`, `png_write_row(s)`, `png_write_image()`, `png_write_end()`.
- Progressive reading: callback registration and `png_process_data()`.
- Memory management: `png_malloc()`, `png_malloc_warn()`, `png_free()`, `png_free_data()`, optional custom allocators.
- Chunk get/set APIs for IHDR, PLTE, bKGD, cHRM, gAMA, hIST, iCCP, oFFs, pCAL, pHYs, sBIT, sCAL, sPLT, sRGB, text, tIME, tRNS, unknown chunks.
- High-level whole-image helpers: `png_read_png()` and `png_write_png()` when `PNG_INFO_IMAGE_SUPPORTED`.

## Internal API Surface

When `PNG_INTERNAL` is defined, this file also declares internal functions used across libpng implementation files:

- Struct allocation/init helpers.
- Default read/write callbacks and zlib allocator callbacks.
- CRC helpers.
- PNG integer load/store helpers.
- Chunk writers for core and ancillary chunks.
- Row lifecycle helpers.
- Read/write transformation functions.
- Chunk handlers for known chunks.
- Progressive-read internal state-machine functions.
- Optional MNG intrapixel and MMX/assembler hooks.

This means `.c` files such as `pngerror.c` include this header with `PNG_INTERNAL` to gain private flags like `PNG_FLAG_STRIP_ERROR_NUMBERS` and private structure visibility.

## Research Notes

For this repository’s filesystem research scope, the important conclusion is negative: this header does not implement storage, VFS, block I/O, or Plan 9 kernel behavior. Its relevance is as a vendored library dependency inside Plan 9’s Ghostscript tree. Any security or maintenance review should treat it as old libpng 1.2.8 API surface, with legacy exposed structs and feature macro ABI sensitivity.
