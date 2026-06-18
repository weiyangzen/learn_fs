# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngread.c

## Purpose

`pngread.c` implements libpng's normal sequential read API. It creates and initializes read structures, reads PNG metadata and image rows, reads trailing chunks, and destroys read-time state.

This is third-party libpng 1.2.8 code vendored in the Plan 9 Ghostscript source tree.

## Main Responsibilities

- Create and initialize `png_struct` for reading.
- Validate application/libpng version compatibility.
- Initialize zlib inflate state and read function pointers.
- Read PNG signature and pre-IDAT metadata chunks.
- Read individual rows, row arrays, or full images.
- Read trailing post-IDAT chunks through `png_read_end()`.
- Free all read-side allocations and reset state.
- Provide convenience API `png_read_png()`.

## Construction and Initialization

`png_create_read_struct()` optionally delegates to `png_create_read_struct_2()` when custom memory callbacks are enabled.

Initialization flow:

- Allocate `png_struct`.
- Initialize optional MMX flags.
- Set user width/height limits when configured.
- Set error and warning handlers.
- Compare `user_png_ver` with `png_libpng_ver`.
- Allocate `zbuf`.
- Set zlib alloc/free callbacks to `png_zalloc` and `png_zfree`.
- Call `inflateInit()`.
- Initialize `zstream.next_out` and `zstream.avail_out`.
- Set default read function via `png_set_read_fn()`.

Deprecated initialization entry points `png_read_init()`, `png_read_init_2()`, and `png_read_init_3()` exist for old applications. They preserve the jump buffer, reset the struct, rebuild zlib state, and warn/error on incompatible struct sizes.

## Metadata Read Path

`png_read_info()`:

- Reads any remaining PNG signature bytes.
- Validates signature and ASCII-conversion corruption.
- Loops over chunks until it reaches `IDAT`.
- Reads chunk length and type, resets CRC, then dispatches to chunk handlers.
- Enforces `IHDR` before `IDAT` and `PLTE` before `IDAT` for palette images.
- Supports known ancillary chunks and unknown-chunk policy.
- Stores first IDAT length in `png_ptr->idat_size` and marks `PNG_HAVE_IDAT`.

Chunk dispatch is a linear chain of `png_memcmp()` checks.

## Row Read Path

`png_read_row()` is the core sequential image decoder.

Key steps:

- Lazily initializes row buffers with `png_read_start_row()`.
- Warns if transformations were requested but not compiled in.
- Handles interlace display rows that do not require a new compressed row.
- Validates that IDAT has been reached.
- Refills zlib input from IDAT chunks into `zbuf`.
- Validates each IDAT CRC before moving to the next chunk.
- Inflates until a full row is available.
- Detects extra compressed data or decompression errors.
- Builds `row_info`.
- Applies PNG row filters if needed.
- Copies current row to `prev_row`.
- Applies optional MNG intrapixel differencing.
- Applies read transformations through `png_do_read_transformations()`.
- Combines rows for interlaced or non-interlaced output.
- Calls `png_read_finish_row()` and optional row status callback.

`png_read_rows()` iterates `png_read_row()` over caller-supplied row/display-row pointer arrays.

`png_read_image()` reads an entire image, calling `png_set_interlace_handling()` when available and looping over passes and rows.

## End Chunk Handling

`png_read_end()` finishes the last IDAT CRC and scans chunks until `IEND`.

It handles:

- `IEND`
- zero-length trailing IDAT legality
- duplicate/nonzero IDAT errors after image data
- known ancillary chunks
- unknown chunks according to configured policy

This function is required by the higher-level `png_read_png()` path to collect trailing metadata.

## Destruction

`png_destroy_read_struct()` coordinates teardown for `png_struct`, `info_ptr`, and `end_info_ptr`, preserving custom memory free callbacks long enough to destroy all objects.

`png_read_destroy()` frees:

- zlib buffer
- row buffers
- previous row
- dithering lookup tables
- gamma tables
- background gamma tables
- palette/transparency/histogram allocations depending on ownership flags
- RFC1123 time buffer
- progressive save buffer and current text state
- zlib inflate state

It then preserves error/warning callbacks and jump buffer, clears `png_struct`, and restores those preserved fields.

## Convenience API

`png_read_png()` performs an all-in-one read:

- Calls `png_read_info()`.
- Applies requested transform flags.
- Updates info through `png_read_update_info()`.
- Allocates `info_ptr->row_pointers` and row buffers if absent.
- Reads the full image.
- Marks `PNG_INFO_IDAT`.
- Calls `png_read_end()`.

It explicitly does not handle background color, gamma transformation, dithering, or filler insertion in the simplified transform switch.

## Research Notes

This file is the sequential counterpart to `pngpread.c`. It owns the blocking stream-oriented read lifecycle and relies on other libpng modules for chunk-specific handling, transformations, row setup, row finishing, filtering, CRC, and I/O.
