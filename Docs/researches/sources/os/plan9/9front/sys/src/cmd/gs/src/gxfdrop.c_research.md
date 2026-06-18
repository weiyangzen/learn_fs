# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfdrop.c

Implements dropout prevention for character rasterization during path filling.

Key behavior:
- Manages `margin` interval lists and `section` arrays used by pseudo-rasterization.
- Uses two moving `margin_set` windows centered on half-pixel Y positions to track thin painted regions around pixel rows.
- `store_margin` inserts and merges touching margin intervals while maintaining ordered linked lists.
- `margin_boundary` records intersections of path boundaries with half-pixel X probes.
- `continue_margin_common`, `margin_interior`, and horizontal-list processing mark candidate dropout areas as fills, boundaries, or interiors.
- `fill_margin` chooses whether to paint an extra pixel row based on recorded upper/lower section contact and serif-adjustment heuristics.
- `close_margins` flushes pending margin intervals to device rectangles.
- `start_margin_set` rotates the two margin sets when the fill loop advances across a pixel-center window.
- Allocates most margins from local `line_list` storage and falls back to GC-managed allocation only if needed.

Dependencies:
- Depends on `gxfill.h` line-list/active-line state and `gxfdrop.h` margin structures.
- Uses `gxdevice.h`, `gxdcolor.h`, and fill rectangle macros to emit corrective pixels.
- Uses `gxfixed.h` fixed-point math and `vdtrace.h` debugging visualization.

Research notes:
- This code only runs for pseudo-rasterized character fills, not normal fills with nonzero adjustment.
- The algorithm targets thin quasi-horizontal stems generated from flattened paths, where normal trapezoid filling may miss a visible pixel.
- `ADJUST_SERIF` and `CHECK_SPOT_CONTIGUITY` are enabled, so serif and spot-contiguity heuristics are active.
