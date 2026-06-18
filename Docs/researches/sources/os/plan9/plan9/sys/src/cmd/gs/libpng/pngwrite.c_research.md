# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngwrite.c

## Summary

`pngwrite.c` contains the main libpng 1.2.8 PNG encoder orchestration code. It writes PNG metadata chunks in the required order, creates and initializes write structs, writes image rows, handles interlaced passes, flushes zlib output, frees write-side resources, configures filters/compression, and provides the high-level `png_write_png` convenience API.

This is not filesystem or storage code. It is third-party PNG encoding code vendored under Plan 9's Ghostscript source tree.

## Main Compile-Time Gates

The file is active under `PNG_WRITE_SUPPORTED`.

Important optional gates include:

- Chunk writers: `PNG_WRITE_gAMA_SUPPORTED`, `PNG_WRITE_sRGB_SUPPORTED`, `PNG_WRITE_iCCP_SUPPORTED`, `PNG_WRITE_sBIT_SUPPORTED`, `PNG_WRITE_cHRM_SUPPORTED`, `PNG_WRITE_tRNS_SUPPORTED`, `PNG_WRITE_bKGD_SUPPORTED`, `PNG_WRITE_hIST_SUPPORTED`, `PNG_WRITE_oFFs_SUPPORTED`, `PNG_WRITE_pCAL_SUPPORTED`, `PNG_WRITE_sCAL_SUPPORTED`, `PNG_WRITE_pHYs_SUPPORTED`, `PNG_WRITE_tIME_SUPPORTED`, `PNG_WRITE_sPLT_SUPPORTED`, `PNG_WRITE_TEXT_SUPPORTED`, `PNG_WRITE_UNKNOWN_CHUNKS_SUPPORTED`.
- Transform and row handling: `PNG_WRITE_INTERLACING_SUPPORTED`, `PNG_WRITE_INVERT_ALPHA_SUPPORTED`, `PNG_WRITE_TRANSFORMS`, `PNG_MNG_FEATURES_SUPPORTED`.
- Runtime/system support: `PNG_USER_MEM_SUPPORTED`, `PNG_SETJMP_SUPPORTED`, `PNG_SET_USER_LIMITS_SUPPORTED`, `PNG_ASSEMBLER_CODE_SUPPORTED`.
- Filter tuning: `PNG_WRITE_WEIGHTED_FILTER_SUPPORTED`.
- Convenience API: `PNG_INFO_IMAGE_SUPPORTED`.

## Metadata Writing

`png_write_info_before_PLTE` writes the PNG signature and the chunks that must appear before `PLTE`.

It writes:

- PNG signature.
- `IHDR`.
- Optional pre-palette chunks such as `gAMA`, `sRGB`, `iCCP`, `sBIT`, `cHRM`.
- Unknown chunks whose recorded location is before `PLTE`.

It sets `PNG_WROTE_INFO_BEFORE_PLTE` to prevent duplicate header emission.

`png_write_info` then writes:

- `PLTE`, with a fatal error if a paletted image has no valid palette.
- `tRNS`, including optional alpha inversion for palette transparency.
- Other pre-IDAT chunks such as `bKGD`, `hIST`, `oFFs`, `pCAL`, `sCAL`, `pHYs`, `tIME`, `sPLT`.
- Header text chunks (`iTXt`, `zTXt`, `tEXt`) according to each text record's compression mode.
- Unknown chunks located after `PLTE` but before `IDAT`.

`png_write_end` writes trailer metadata after image data and then emits `IEND`. It requires that at least one IDAT has been written.

## Struct Creation and Initialization

`png_create_write_struct` and `png_create_write_struct_2` allocate and initialize a `png_struct` for writing.

Key setup steps:

- Allocate the structure through libpng's normal or user-memory allocator.
- Initialize MMX flags when assembler code is enabled.
- Set user width/height limits when supported.
- Establish error handling and `setjmp` fallback behavior.
- Check runtime libpng version compatibility against the application header version.
- Allocate the zlib output buffer `zbuf`.
- Install default write callbacks through `png_set_write_fn`.
- Initialize weighted filter heuristics when enabled.

Legacy entry points `png_write_init`, `png_write_init_2`, and `png_write_init_3` support applications compiled against older libpng APIs. They validate structure sizes, preserve the jump buffer, reset the structure, and then perform write initialization.

## Row and Image Writing

`png_write_rows` writes a caller-supplied sequence of rows by repeatedly calling `png_write_row`.

`png_write_image` writes a full image and handles Adam7 interlace pass repetition when `png_set_interlace_handling()` is active.

`png_write_row` is the core row pipeline:

1. On the first row/pass, verify header info was written and call `png_write_start_row`.
2. Warn about requested write transforms that were compiled out.
3. Skip rows not used by the current Adam7 pass.
4. Populate `png_ptr->row_info` from user-visible image parameters.
5. Copy the user row into `png_ptr->row_buf + 1`, leaving byte 0 for the PNG filter type.
6. Apply write interlace reduction through `png_do_write_interlace` when needed.
7. Apply configured row transformations through `png_do_write_transformations`.
8. Apply MNG intrapixel differencing when permitted.
9. Pick/filter/compress/write the row through `png_write_find_filter`.
10. Call the optional write status callback.

This function coordinates with `pngwtran.c` for transformations and `pngwutil.c` for row setup, interlace reduction, filter selection, and chunk emission.

## Flushing

When `PNG_WRITE_FLUSH_SUPPORTED` is enabled:

- `png_set_flush` sets the automatic flush interval.
- `png_write_flush` uses `deflate(..., Z_SYNC_FLUSH)` to push pending compressed data into IDAT chunks, resets zlib output pointers, clears `flush_rows`, and calls `png_flush`.

Compression errors are fatal.

## Destruction

`png_destroy_write_struct` frees the info struct and write struct, preserving user-memory allocator hooks when configured.

`png_write_destroy` releases write-side allocations:

- zlib stream state via `deflateEnd`.
- `zbuf`, `row_buf`, `prev_row`, and filter candidate rows.
- RFC1123 time buffer when present.
- Weighted filter heuristic arrays when present.

It then clears most of `png_struct` while preserving error/warning callbacks, error pointer, optional custom free function, and jump buffer.

## Filter and Compression Configuration

`png_set_filter` selects allowed PNG row filters for method `PNG_FILTER_TYPE_BASE`.

It supports:

- None
- Sub
- Up
- Average
- Paeth
- Bitmask combinations of the above

If filters are changed after row buffers have already been allocated, it lazily allocates missing filter buffers where possible. It refuses to add filters requiring `prev_row` if previous-row state is unavailable.

`png_set_filter_heuristics` configures weighted filter selection:

- Validates heuristic method.
- Allocates and initializes previous-filter history.
- Stores filter weights and inverse weights.
- Allocates per-filter costs and inverse costs.

Compression setter APIs store zlib preferences in `png_ptr` and mark corresponding custom flags:

- `png_set_compression_level`
- `png_set_compression_mem_level`
- `png_set_compression_strategy`
- `png_set_compression_window_bits`
- `png_set_compression_method`

The window-bits setter warns for PNG-incompatible sizes and may adjust an 8-bit window to 9 if `WBITS_8_OK` is not defined.

## High-Level Convenience API

`png_write_png` performs a complete write from a populated `png_info`:

1. Applies pre-info alpha inversion if requested.
2. Calls `png_write_info`.
3. Enables requested write transforms such as invert mono, shift, packing, swap alpha, strip filler, BGR, endian swap, and packswap.
4. Writes `info_ptr->row_pointers` if image data is present.
5. Calls `png_write_end`.

The `params` argument is unused except to quiet warnings in this vintage API.

## Dependencies

This file depends heavily on other libpng internals:

- `pngwio.c`: `png_set_write_fn`, `png_flush`.
- `pngwutil.c`: chunk writers, `png_write_start_row`, `png_do_write_interlace`, `png_write_find_filter`, `png_write_finish_row`.
- `pngwtran.c`: `png_do_write_transformations`.
- zlib: `deflate`, `deflateEnd`, output buffer management.
- Core allocation/error/version helpers from `png.c` and `pngmem.c`.

## Research Notes

`pngwrite.c` is the write-side control plane for this vendored libpng. It does not implement storage persistence itself; it emits bytes through callbacks configured in `pngwio.c`. The highest-risk areas are chunk ordering, row/interlace state transitions, legacy initialization compatibility, and zlib flush/finalization behavior.
