# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbitops.h

## Role

`gsbitops.h` is the public Ghostscript bitmap/packed-sample operations interface. It is a header-only macro layer for reading and writing packed pixel/component samples plus prototypes for byte/bit rectangle operations.

This is graphics infrastructure, not filesystem code.

## Main Interfaces

- Packed sample load macros:
  - `sample_load8`, `sample_load12`, `sample_load16`, `sample_load32`, `sample_load64`
  - `sample_load_next*`
  - `sample_load_any`, selected by `sizeof(value)`
- Packed sample store macros:
  - `sample_store_next8`, `sample_store_next12`, `sample_store_next16`, `sample_store_next32`, `sample_store_next64`
  - `sample_store_next_any`
  - `sample_store_flush`, `sample_store_skip_next`
- Positioning helpers:
  - `sample_load_setup`
  - `sample_store_setup`
  - `sample_next`
- Bitmap/byte operation prototypes:
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

## Data Structures

- `bits_plane_t` describes one plane of a pixmap/bitmap:
  - `data.write` or `data.read`
  - `raster`
  - `depth`
  - `x`

## Important Behavior

- Supports bits-per-value of `1`, `2`, `4`, `8`, `12`, `16`, `24`, `32`, and larger byte-aligned values up to 64-bit paths.
- Bit numbering is documented as big-endian inside a byte: `0x80` is bit 0, `0x01` is bit 7.
- `sample_bound_shift` avoids compiler warnings or undefined large shifts by masking shifts that exceed the storage width.
- Store macros preserve partial destination bytes with `sample_store_preload` and `sample_store_flush`.
- The macros assume Ghostscript block macros such as `BEGIN`, `END`, and `return_error(...)` are available in the including context.

## Dependencies And Assumptions

- Uses Ghostscript scalar types such as `byte`, `uint`, `gx_color_index`, `gs_int_rect`, and `gs_log2_scale_point`.
- Uses architecture constants such as `arch_sizeof_int`.
- The `sample_end_` macro returns `gs_error_rangecheck` on unsupported sample widths, so the load/store macros are intended for functions returning an integer error code.

## Notable Risks

- Macro-heavy implementation has hidden control flow, including `return_error`, switch fall-through in store paths, and pointer increments.
- Correctness depends on caller-provided bit positions and raster alignment.
- Multi-byte sample paths assume big-endian byte ordering in the encoded data.
