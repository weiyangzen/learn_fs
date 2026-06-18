# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbitmap.h

Defines internal bitmap, tile bitmap, and shifted strip bitmap types and alignment/raster rules.

Key definitions:
- `gx_bitmap_id` aliases `gs_bitmap_id`; `gx_no_bitmap_id` aliases the public no-ID value.
- `align_bitmap_mod` is derived from platform long alignment, and `bitmap_raster(width_bits)` rounds scanline storage up to required alignment.
- Defines mutable and const `gx_bitmap` structures using the public bitmap common layout.
- Defines mutable and const tile bitmap structures.
- Defines strip bitmap structures for halftones at arbitrary angles, with `rep_shift` and cached aggregate `shift`.
- Documents how shifted strip halftones map device `(X,Y)` into repeated/shifted bitmap coordinates.
- Provides GC structure descriptor macros for `gx_strip_bitmap`.

Research notes:
- The header emphasizes both alignment and padding requirements: code may legally access bytes past the last meaningful byte up to alignment padding.
- Shifted strip requirements restrict `rep_shift`, effective shift, and stored height to avoid ambiguous full-tile cases.
