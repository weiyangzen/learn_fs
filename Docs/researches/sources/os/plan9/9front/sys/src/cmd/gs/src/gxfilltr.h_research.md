# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfilltr.h

Template header that generates trapezoid decomposition fill-loop variants.

Key behavior:
- Defines `TEMPLATE_spot_into_trapezoids(line_list *, fixed band_mask)` under macro control.
- Moves edges from Y-sorted pending list into X-sorted active list as the sweep advances.
- Handles isolated horizontal segments directly or records them for pseudo-rasterization.
- Computes next Y band from pending starts, edge ends, band masks, and intersections.
- Uses `intersect_al` to split bands at crossings.
- Generates fill regions using winding/even-odd inside transitions.
- Emits rectangles for vertical-sided regions, trapezoids for slanted regions, and spot-analyzer trap records for spot-analysis devices.
- Calls slanted-adjust helpers when fill adjustment requires expanded trapezoid geometry.
- Integrates pseudo-rasterization by starting/closing margin sets, processing horizontal lists, and recording margins/interiors around filled trapezoids.

Template parameters:
- `IS_SPOTAN`
- `PSEUDO_RASTERIZATION`
- `FILL_ADJUST`
- `FILL_DIRECT`
- `TEMPLATE_spot_into_trapezoids`

Dependencies:
- Included repeatedly by `gxfill.c`.
- Relies on `gxfill.c` helpers such as `insert_x_new`, `move_al_by_y`, `process_h_segments`, `intersect_al`, `complete_margin`, and `process_h_lists`.

Research notes:
- This is the hot path for most non-scanline fills.
- The macro specializations remove runtime branches for the common combinations of spot analysis, pseudo-rasterization, fill adjustment, and direct color writes.
