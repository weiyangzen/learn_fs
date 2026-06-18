# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfilltr.h

## Purpose
Template header for generating trapezoid decomposition fill loops. `gxfill.c` includes it repeatedly to create specialized functions for spot analysis, pseudo-rasterization, fill adjustment, and direct/non-direct color writes.

## Template Inputs
- `IS_SPOTAN`: output trapezoids to spot analyzer instead of normal device fill.
- `PSEUDO_RASTERIZATION`: enable dropout-prevention margin tracking.
- `FILL_ADJUST`: include fill adjustment in geometry and raster decisions.
- `FILL_DIRECT`: choose direct rectangle fills or ROP-aware fills.
- `TEMPLATE_spot_into_trapezoids`: generated function name.

## Algorithm
- Pulls pending lines from `y_list` into X-sorted active state at each Y.
- Handles isolated horizontal lines specially.
- Computes next band top from segment ends, new segment starts, band limits, and intersections.
- Uses winding/even-odd accumulation to pair left/right boundaries.
- Emits rectangles for vertical-sided regions and trapezoids for slanted regions.
- Calls slanted-adjust helpers when fill adjustment needs more precise decomposition.
- In pseudo-rasterization mode, calls margin/dropout helpers around every filled or skipped band.

## Spot Analyzer Path
When `IS_SPOTAN` is enabled, stores trapezoid topology through `gx_san_trap_store` rather than painting directly, preserving segment pointers and boundary directions.

## Dropout Path
When `PSEUDO_RASTERIZATION` is enabled, invokes:
- `start_margin_set`
- `complete_margin`
- `margin_interior`
- `add_margin`
- `process_h_lists`
- `close_margins`

## Notable Characteristics
The generated loops are highly optimized by compile-time macros and avoid runtime conditionals for common fill modes.
