# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfillts.h

## Purpose
Template header for generating slanted-trapezoid fill-adjustment helpers. It is included by `gxfill.c` for direct and non-direct rectangle fill variants.

## Template Inputs
- `FILL_DIRECT`: direct device fill versus ROP-aware fill.
- `TEMPLATE_slant_into_trapezoids`: generated helper name.

## Algorithm
Handles the geometry produced by dragging an adjustment square along trapezoid borders. It distinguishes:
- top wider than bottom,
- bottom wider than top,
- genuinely slanted trapezoids requiring `fill_slant_adjust`.

## Key Details
- Uses adjusted left/right edges and `adjust_below`/`adjust_above`.
- Adds single-row rectangle repairs where adjusted top or bottom spans an additional pixel.
- Uses `loop_fill_trap_np` for clipped trapezoid fills that do not require pseudo-rasterization.

## Integration
Called from adjusted trapezoid loops in `gxfilltr.h` when a filled region has slanted boundaries and vertical fill adjustment is active.
