# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfdrop.c

## Purpose
Implements dropout prevention for character rasterization in the path fill algorithm. It tracks thin quasi-horizontal stems during pseudo-rasterization and paints one-pixel repairs where normal trapezoid filling would leave visual gaps.

## Main Data Flow
- Maintains two active `margin_set` windows, each corresponding to a half-integer pixel-row sampling window.
- Each margin set has an ordered linked list of horizontal intervals (`margin`) and an array of per-X `section` samples.
- Filling code calls into this file while trapezoid bands are generated.
- When a margin window closes, `fill_margin` decides which pixels to paint and emits rectangles through the device fill path.

## Key Functions
- `init_section`: resets section state over an interval.
- `free_all_margins`: frees dynamically allocated margin records and clears the reusable list.
- `store_margin`: inserts/merges margin intervals in ordered form.
- `margin_boundary`: samples boundary intersections at half-integer X positions.
- `continue_margin_common`: records both sides of an active filled region into a margin set.
- `margin_interior`: marks fully painted interior pixels so dropout repair does not overpaint them.
- `process_h_lists`: handles horizontal path segments that form margin boundaries.
- `close_margins`: fills all pending margin intervals and releases their list.
- `start_margin_set`: advances the rolling pair of margin windows.

## Algorithms / Heuristics
- Uses `ADJUST_SERIF` and `CHECK_SPOT_CONTIGUITY` to reduce bad serif widening in small poorly hinted fonts.
- Computes padding from section `y0`/`y1` to decide whether to paint the lower or upper pixel in the row window.
- Treats interior coverage as `-2` sentinel values to suppress repair pixels where normal trapezoids already cover the spot.
- Reuses local margin storage first and falls back to GC allocation only when active margins exceed `MAX_LOCAL_ACTIVE`.

## Dependencies
Works tightly with `gxfill.c` and `gxfill.h` structures (`line_list`, `active_line`, `fill_options`), fixed-point math from `gxfixed.h`, devices/colors, and optional `vdtrace` debugging visualization.

## Notable Risks / Edge Cases
The code is intentionally heuristic and contains comments noting imperfect handling for bold characters and contacting serifs. It assumes no garbage collection while transient margins are active and uses simple GC descriptors accordingly.
