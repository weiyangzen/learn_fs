# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfillsl.h

Template header that generates scanline fill-loop variants.

Key behavior:
- Defines `TEMPLATE_spot_into_scanlines(line_list *, fixed band_mask)` under caller-supplied macro names.
- Supports direct pure-color rectangle fills or RasterOp-aware fills through `FILL_DIRECT`.
- Maintains a `coord_range_list_t` of X ranges for each output scanline.
- Advances active lines by sampling Y bands derived from fill adjustment values.
- Inserts newly active non-horizontal edges into the X list.
- Uses winding or even-odd fill logic through `INSIDE_PATH_P`.
- Calls `merge_ranges` to include regions contributed by active segments across the same pixel band.
- Flushes merged ranges as one-pixel-high rectangles.

Template parameters:
- `FILL_DIRECT`
- `TEMPLATE_spot_into_scanlines`

Dependencies:
- Must be included from `gxfill.c`, where helper types/functions and range-list machinery are defined.

Research notes:
- This file is intentionally not include-guarded as a normal header because it is included multiple times with different macro definitions.
- The scanline path is important when non-idempotent RasterOps or fill adjustment make trapezoid double-writing unsafe.
