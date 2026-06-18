# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclip2.c

## Purpose
Implements tiled mask clipping for patterns. It adapts the general mask clipping infrastructure to repeated tile masks with explicit phase handling.

## Main Responsibilities
- Defines the `"tile clipper"` device descriptor.
- Initializes tiled clip devices with `tile_clip_initialize`.
- Stores and updates tile phase with `tile_clip_set_phase`.
- Clips fill/copy operations through a repeated mask tile.
- Scans tile bits into runs for non-monochrome operations.

## Key Implementation Details
- `tile_clip_initialize` delegates base setup to `gx_mask_clip_initialize`, then records tile metadata and phase.
- `x_offset` accounts for tile phase and `rep_shift` across repeated tile rows.
- `tile_clip_fill_rectangle` forwards directly as `strip_tile_rectangle`.
- `tile_clip_copy_mono` intersects source bits with tile mask in a memory device buffer, then forwards the combined mask.
- `FOR_RUNS` macro scans repeated tile rows for runs of set bits and forwards those runs.

## Forwarded Operations
- `copy_color`
- `copy_alpha`
- `strip_copy_rop`
- `copy_mono` through a temporary mask intersection path
- `fill_rectangle` through strip tiling

## Dependencies
- `gxclip2.h` for type/interface.
- `gxmclip.h` via header for shared mask clip state.
- `gxdevmem.h` for memory device buffering.

## Research Notes
This file is specialized for repeated pattern masks. It trades generic clip-list enumeration for bit-run scanning over the tile bitmap and phase-adjusted repetition.
