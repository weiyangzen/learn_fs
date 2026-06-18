# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfdrop.h

## Purpose
Declares the dropout-prevention data structures and entry points shared between the fill algorithm and `gxfdrop.c`.

## Main Types
- `margin`: linked-list interval `[ibeg, iend)` of pixels to consider for repair.
- `section`: per-X sampling record containing fractional `y0`/`y1` boundary intersections, plus optional `x0`/`x1` coverage when serif/contiguity adjustment is enabled.
- `margin_set`: one row-window state with sampling Y coordinate, margin list, touched margin cache, and section array.

## Configuration
- `ADJUST_SERIF` is enabled.
- `CHECK_SPOT_CONTIGUITY` is enabled.
These control extra logic for small serif and stem repair choices.

## Public Functions
- `init_section`
- `free_all_margins`
- `close_margins`
- `process_h_lists`
- `margin_interior`
- `start_margin_set`
- `continue_margin_common`

## Integration
This header forward-declares `active_line` and `line_list`, showing it is intentionally coupled to the fill loop internals rather than being a standalone raster module.
