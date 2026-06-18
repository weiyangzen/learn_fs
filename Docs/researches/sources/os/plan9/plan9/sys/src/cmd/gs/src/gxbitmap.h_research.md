# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbitmap.h

Purpose: Defines Ghostscript internal bitmap, tile bitmap, and shifted-strip bitmap structures and alignment/raster rules.

Key definitions:
- `gx_bitmap_id` aliases `gs_bitmap_id`; `gx_no_bitmap_id` aliases `gs_no_bitmap_id`.
- `align_bitmap_mod` derives required scan-line alignment from long alignment.
- `bitmap_raster(width_bits)` rounds bit width up to aligned byte raster.
- `gx_bitmap`, `gx_const_bitmap`, `gx_tile_bitmap`, `gx_const_tile_bitmap`.
- `gx_strip_bitmap` and `gx_const_strip_bitmap` add `rep_shift` and `shift` for shifted halftone strips.
- Structure descriptor macro `public_st_gx_strip_bitmap()`.

Behavior:
- Documents that scan lines must start aligned and must have padding bytes available for chunk-based operations.
- Describes shifted strip halftones: each repeated strip may shift horizontally as Y advances.
- `shift` is an accelerator derived from repeated strip shift and stored bitmap height.

Dependencies:
- Includes `gstypes.h` and `gsbitmap.h`.

Notable risks:
- Many rendering routines assume padding bytes are addressable even beyond logical pixel data.
- Strip bitmap invariants must hold: `rep_shift < rep_width` and consistent derived `shift`.
