# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngread.c

## Role

`pngread.c` implements the public sequential PNG read API for libpng 1.2.8. It creates and initializes read structs, reads metadata chunks, reads image rows from IDAT data, reads trailing chunks, and destroys read-side allocations.

## Main APIs and Behavior

- `png_create_read_struct()` / `png_create_read_struct_2()` allocate `png_struct`, set error/memory hooks, check libpng version compatibility, allocate the zlib buffer, initialize inflate state, and install default read I/O.
- Deprecated initialization compatibility:
  - `png_read_init()`
  - `png_read_init_2()`
  - `png_read_init_3()`
- `png_read_info()` validates the PNG signature and reads chunks until the first `IDAT`.
- `png_read_update_info()` initializes rows if needed and updates `info_ptr` to reflect configured transformations.
- `png_start_read_image()` ensures row state is initialized before row reads.
- `png_read_row()` reads one image row:
  - Handles interlace skip/combine behavior.
  - Pulls IDAT data into `zbuf`.
  - Runs `inflate()`.
  - Applies PNG row filters.
  - Copies current row to `prev_row`.
  - Applies optional MNG intrapixel differencing.
  - Applies read transformations.
  - Combines interlaced rows into caller buffers.
  - Calls optional row status callback.
- `png_read_rows()` reads multiple rows.
- `png_read_image()` reads the full image, including all interlace passes if enabled.
- `png_read_end()` consumes chunks after image data through `IEND`.
- `png_destroy_read_struct()` frees `png_struct`, `info_ptr`, and optional end-info.
- `png_read_destroy()` frees read-side internal allocations and resets preserved error/jump state.
- `png_set_read_status_fn()` installs a per-row status callback.
- `png_read_png()` is a convenience wrapper that reads the whole PNG into `info_ptr->row_pointers` after applying selected simple transforms.

## Chunk Flow

`png_read_info()` reads the signature, then loops over chunk length/name pairs. It dispatches known chunks by linear name comparison and stops at the first `IDAT`, after validating required ordering:

- `IHDR` must precede `IDAT`.
- Palette images require `PLTE` before `IDAT`.
- Unknown chunks are delegated to unknown-chunk handling, including user callbacks when enabled.

`png_read_end()` finishes the last IDAT CRC, then reads trailing chunks until `IEND`. Nonzero IDAT data after image completion is rejected.

## Row Decode Flow

`png_read_row()` is the sequential row pipeline:

1. Ensure row buffers are initialized.
2. Skip or combine Adam7 rows that do not need fresh compressed data.
3. Ensure current chunk is IDAT.
4. Read compressed bytes into `zbuf`, with CRC accounting.
5. Inflate into `row_buf`.
6. Decode PNG row filter using `prev_row`.
7. Save current row as previous row.
8. Apply MNG intrapixel reversal if configured.
9. Apply read transformations from `pngrtran.c`.
10. Interlace-combine into caller buffers.
11. Advance row/pass state.

## Dependencies

- `pngrio.c` for `png_read_data()` and default/custom read callbacks.
- `pngmem.c` allocation wrappers.
- zlib inflate APIs.
- Chunk handlers from other libpng files.
- Row filtering and interlace helpers.
- Transform implementation from `pngrtran.c`.
- Error handling with `setjmp` when enabled.

## State Mutated

- `png_ptr` lifecycle fields, error handlers, memory handlers, jump buffer.
- zlib state: `zstream`, `zbuf`, `zbuf_size`.
- read flags/modes: `PNG_HAVE_IDAT`, `PNG_AFTER_IDAT`, `PNG_HAVE_IEND`, etc.
- row state: `row_buf`, `big_row_buf`, `prev_row`, `row_number`, `pass`, `num_rows`.
- transform-related state via calls to transform setup/update functions.
- `info_ptr` metadata and row pointers in `png_read_png()`.

## Cleanup Coverage

`png_read_destroy()` frees:

- zlib buffer.
- big row buffer and previous row.
- dither lookup/index tables.
- gamma tables.
- background gamma tables.
- owned palette, transparency, histogram.
- RFC1123 time buffer.
- progressive save buffer and current text.
- zlib inflate state.

It then zeroes `png_struct` while preserving error functions, warning functions, error pointer, free function, and jump buffer.

## Risks and Maintenance Notes

- The API relies on longjmp-style fatal error handling when `PNG_SETJMP_SUPPORTED` is enabled.
- `png_destroy_read_struct()` stores `png_ptr->free_fn` and `png_ptr->mem_ptr` under `PNG_USER_MEM_SUPPORTED`, so callers must not pass a null `png_ptr` through that path.
- Chunk dispatch is intentionally linear and old-style; comments note a hash or binary search would be better.
- The row path is tightly coupled to transform order and row buffer sizing initialized elsewhere.
- `png_read_png()` allocates all rows and can reject very tall images only with a height * pointer-size overflow check; memory pressure is otherwise handled by allocator failure paths.

## Research Summary

This file is the normal pull-mode reader. It wires together I/O, chunk parsing, zlib decompression, row filtering, transformation, interlace handling, full-image convenience loading, and read-side cleanup.
