# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfillsl.h

## Purpose
Template header for generating scanline-based path fill loops. It is included multiple times by `gxfill.c` with different macro parameters.

## Template Inputs
- `FILL_DIRECT`: selects direct device rectangle writes or ROP-aware rectangle writes.
- `TEMPLATE_spot_into_scanlines`: generated function name.

## Algorithm
- Maintains active lines in X order.
- Computes Y sampling bands using adjustment-derived fractional limits.
- Uses fill rule accumulation (`INSIDE_PATH_P`) to determine filled X intervals.
- Merges ranges into `coord_range_list_t`.
- Emits one-pixel-high rectangles for each completed scanline range.
- Calls `merge_ranges` to include path portions spanning the current sample band.

## Integration
Relies on support routines and types defined in `gxfill.c` before inclusion: active-line management, range lists, fill options, and rectangle fill macros.

## Notable Characteristics
Unlike the trapezoid backend, this backend is designed to avoid repeated writes to the same pixel row when fill adjustment or non-idempotent RasterOps make overdraw unsafe.
