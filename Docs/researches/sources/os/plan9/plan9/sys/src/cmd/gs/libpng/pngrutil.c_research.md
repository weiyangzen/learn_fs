# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngrutil.c

`pngrutil.c` contains libpng's internal read-side utilities. It handles endian decoding, CRC handling, ancillary/critical chunk parsing, compressed text/profile decompression, unknown chunk dispatch, interlace row expansion, adaptive filter reversal, and row-buffer setup/finish logic.

Key responsibilities:
- Provides big-endian scalar readers: `png_get_uint_31`, `png_get_uint_32`, `png_get_int_32`, and `png_get_uint_16`.
- Wraps chunk data reads with CRC updates through `png_crc_read`, `png_crc_finish`, and `png_crc_error`.
- Decompresses compressed ancillary chunk payload tails through `png_decompress_chunk` for zTXt/iTXt/iCCP-style data.
- Implements handlers for core and ancillary chunks: `IHDR`, `PLTE`, `IEND`, `gAMA`, `sBIT`, `cHRM`, `sRGB`, `iCCP`, `sPLT`, `tRNS`, `bKGD`, `hIST`, `pHYs`, `oFFs`, `pCAL`, `sCAL`, `tIME`, `tEXt`, `zTXt`, `iTXt`, and unknown chunks.
- Implements scanline helpers: `png_combine_row`, `png_do_read_interlace`, `png_read_filter_row`, `png_read_finish_row`, and `png_read_start_row`.

Chunk parsing behavior:
- Most handlers enforce PNG ordering: required `IHDR` first, many metadata chunks before `IDAT`, and no duplicate metadata chunks when the matching `PNG_INFO_*` valid bit is already set.
- Critical chunks generally call `png_error` on structural invalidity; ancillary chunks often warn and skip.
- CRC behavior is governed by `PNG_FLAG_CRC_*` flags, with separate handling for ancillary and critical chunks.
- `png_handle_IHDR` reads the 13-byte header, initializes core `png_struct` image fields, computes `channels`, `pixel_depth`, and `rowbytes`, then delegates validation/storage to `png_set_IHDR`.
- Palette and transparency handlers coordinate with `png_set_PLTE` and `png_set_tRNS`, including truncation warnings when tRNS exceeds the actual palette length.
- Color-management handlers cross-check sRGB with gAMA/cHRM values and ignore inconsistent values with warnings.
- Text/profile handlers allocate full chunk buffers, split NUL-delimited fields, optionally decompress payloads, populate `png_text`, `iCCP`, or related structures, and free temporary buffers after `png_set_*` copies data.
- `png_handle_unknown` validates chunk names, rejects unhandled critical chunks unless configured/user-handled, optionally stores unknown chunks, invokes user chunk callbacks, and then finishes CRC/skipping.

Scanline and image-data behavior:
- `png_combine_row` merges the newly decoded row into the user row for interlaced/progressive display, with separate paths for 1-, 2-, 4-bit packed pixels and byte-aligned pixels.
- `png_do_read_interlace` expands Adam7 pass rows in place, again specializing packed bit depths and byte-aligned pixels.
- `png_read_filter_row` reverses PNG filter types None, Sub, Up, Average, and Paeth.
- `png_read_finish_row` advances row/pass state, drains remaining zlib data at image end, validates continued `IDAT` availability, warns on extra compressed data, resets inflate state, and marks `PNG_AFTER_IDAT`.
- `png_read_start_row` initializes read transformations, calculates pass dimensions, estimates maximum transformed pixel depth, allocates `big_row_buf`, `row_buf`, and `prev_row`, and sets `PNG_FLAG_ROW_INIT`.

Important dependencies and state:
- Includes `png.h` with `PNG_INTERNAL`.
- Uses zlib `inflate`, `inflateReset`, and `zstream` fields in `png_struct`.
- Relies on `png_set_*` routines in `pngset.c`, memory helpers, warning/error callbacks, CRC helpers, mode flags, transformation flags, and compile-time feature macros.

Edge cases and risks:
- This is older libpng 1.2.8 code with many feature-macro branches and 64K allocation compatibility paths.
- Several chunk parsers scan NUL-delimited data manually; malformed chunks are mostly handled by warning/return, but maintenance must preserve exact bounds and CRC-skipping behavior.
- `png_handle_sPLT` allocates `new_palette.entries`; on some early error paths after allocation-size checks, freeing must remain carefully paired.
- `png_read_start_row` row-size calculations are security-sensitive because they allocate scanline buffers based on transformed maximum pixel depth.
- The file is core decoder attack surface: chunk length checks, allocation limits, zlib state transitions, and row filter math are the most important review areas.
