# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbitops.h

Header defining Ghostscript bitmap and packed-sample bit manipulation interfaces.

Key contents:
- Provides macros for loading and storing packed sample values at 1, 2, 4, 8, 12, 16, 24, 32, and up to 64 bits per value.
- Uses big-endian bit numbering within bytes for setup semantics, with `sample_next` advancing a byte pointer plus bit offset.
- Defines store-side helpers for preloading/flushing partial destination bytes.
- Defines `mono_fill_chunk`, `mono_fill_chunk_bytes`, and `mono_fill_make_pattern` for monobit rectangle fills.
- Declares rectangle/plane operations:
  - `bits_fill_rectangle`
  - `bits_fill_rectangle_masked`
  - `bits_replicate_horizontally`
  - `bits_replicate_vertically`
  - `bits_bounding_box`
  - `bits_compress_scaled`
  - `bits_extract_plane`
  - `bits_expand_plane`
  - `bytes_fill_rectangle`
  - `bytes_copy_rectangle`
- Defines `bits_plane_t`, which describes aligned source/destination bit planes with data pointer, raster, depth, and starting x offset.

Important implementation notes:
- The load/store macros expand into switch statements and are intended for performance-sensitive inner loops.
- Invalid sample depths return `gs_error_rangecheck` through `sample_end_`, so callers must use the macros in functions where `return_error` is available.
- 64-bit sample helpers use `gx_color_index` and `sample_bound_shift` to avoid compiler warnings or undefined shifts on narrower integer types.
- This is an interface-only file; implementations are elsewhere in Ghostscript bit operation sources.
