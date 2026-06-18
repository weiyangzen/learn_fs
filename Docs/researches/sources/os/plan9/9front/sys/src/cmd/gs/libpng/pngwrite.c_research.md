# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngwrite.c

Implements the main libpng write lifecycle: header chunks, rows, compression flushing, teardown, filter selection, compression settings, and the simplified `png_write_png()` API.

Key points:
- Compiles under `PNG_WRITE_SUPPORTED`.
- `png_write_info_before_PLTE()` writes the PNG signature and pre-PLTE chunks:
  - IHDR is always written.
  - Optional chunks include `gAMA`, `sRGB`, `iCCP`, `sBIT`, `cHRM`, and pre-PLTE unknown chunks.
  - Guards MNG-only feature use in normal PNG datastreams.
- `png_write_info()` writes PLTE and other pre-IDAT metadata:
  - Requires a valid palette for paletted images.
  - Writes `tRNS`, `bKGD`, `hIST`, `oFFs`, `pCAL`, `sCAL`, `pHYs`, `tIME`, `sPLT`, text chunks, and location-appropriate unknown chunks.
  - Can invert palette alpha in `tRNS` when `PNG_INVERT_ALPHA` is active.
- `png_write_end()` finalizes the stream:
  - Requires that IDAT data was written.
  - Writes trailing `tIME`, text, and post-IDAT unknown chunks when present.
  - Sets `PNG_AFTER_IDAT` and writes IEND.
- Time helpers convert `struct tm` and `time_t` into `png_time`.
- `png_create_write_struct()` and `png_create_write_struct_2()` allocate and initialize `png_struct`:
  - Set error/memory callbacks.
  - Check library/header version compatibility.
  - Initialize MMX flags when assembler support is enabled.
  - Set user dimension limits.
  - Allocate the zlib output buffer.
  - Configure default write callbacks.
  - Initialize weighted filter heuristics when supported.
- Legacy `png_write_init()`, `png_write_init_2()`, and `png_write_init_3()` support old applications that allocated structs themselves.
- `png_write_rows()` and `png_write_image()` drive row writing, with multi-pass handling for interlaced images.
- `png_write_row()` is the central row pipeline:
  - Verifies `png_write_info` was called.
  - Initializes write state on the first row.
  - Skips rows not used by the current Adam7 pass.
  - Builds `row_info` from user-facing row format.
  - Copies the user row into `row_buf + 1`, preserving byte 0 for the filter type.
  - Applies write interlace reduction, configured write transformations, optional MNG intrapixel differencing, filter selection, compression/write, and row status callback.
- Flush support:
  - `png_set_flush()` configures automatic row flush distance.
  - `png_write_flush()` uses `deflate(..., Z_SYNC_FLUSH)`, writes pending IDAT chunks, resets zlib output state, and calls the output flush callback.
- Destruction:
  - `png_destroy_write_struct()` frees info data, unknown chunk lists, write buffers, zlib state, and structs.
  - `png_write_destroy()` releases write-side buffers while preserving error/jump callback state.
- `png_set_filter()` selects permitted PNG row filters and lazily allocates filter buffers if row writing already started.
- Weighted filter heuristics allocate and configure previous-filter history, filter weights, inverse weights, costs, and inverse costs.
- Compression setters store custom zlib settings on `png_ptr`: level, memory level, strategy, window bits, and method.
- `png_set_write_status_fn()` installs a per-row callback.
- `png_set_write_user_transform_fn()` enables and stores a user transform callback.
- `png_write_png()` is the high-level convenience API:
  - Applies requested transform flags.
  - Writes info, image rows from `info_ptr->row_pointers`, and end chunks.

Dependencies and interactions:
- Calls chunk writers from `pngwutil.c` such as `png_write_IHDR`, `png_write_PLTE`, `png_write_IDAT`, and ancillary chunk writers.
- Uses writer transforms from `pngwtran.c`, filter selection/compression helpers, zlib `deflate`, and output callbacks from `pngwio.c`.
- Relies on many compile-time feature flags for optional chunk types, transforms, stdio, user memory, setjmp, MNG behavior, and weighted filtering.

Research relevance:
- This is the main public write API implementation for the bundled libpng.
- It defines the required call ordering and state transitions for producing a PNG: create/init, configure callbacks/options, write info, write rows/image, write end, destroy.
