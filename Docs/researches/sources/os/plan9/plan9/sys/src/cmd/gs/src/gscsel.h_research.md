# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscsel.h

## Purpose
Defines color operand selection for RasterOp/source-texture color mapping.

## Key Contents
- `gs_color_select_all = -1` for setting only.
- `gs_color_select_texture = 0`.
- `gs_color_select_source = 1`.
- `gs_color_select_count = 2`.

## Important Details
- Comments note source and texture currently mainly differ by halftone phase, but may diverge more in the future.
- Texture selection value `0` is aligned with `currenthtphase`.

## Research Notes
This is a small shared enum header used by remap/color APIs.
