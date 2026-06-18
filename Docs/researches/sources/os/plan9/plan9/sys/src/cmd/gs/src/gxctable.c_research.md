# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxctable.c

## Purpose
Implements lookup and interpolation for 3-D and 4-D color lookup tables.

## Public Surface
- `gx_color_interpolate_nearest(...)`: returns nearest table entries without interpolation.
- `gx_color_interpolate_linear(...)`: returns linearly interpolated output values.

## Implementation
- Nearest lookup rounds fixed-point input indices and copies `m` byte table values as `frac` outputs.
- Linear interpolation delegates to `interpolate_accum`.
- For 4-D tables, interpolation performs two 3-D interpolations and interpolates between them on the first coordinate.
- For 3-D tables, it gathers the eight neighboring samples, interpolates along c, then b, then a, using fixed-point fractional parts.
- Boundary coordinates use zero deltas at the high edge to avoid reading past the last table entry.

## Dependencies
Uses fixed-point helpers, fraction conversion macros, and the `gx_color_lookup_table` structure from `gxctable.h`.

## Risks and Notes
- The code assumes caller-supplied indices are already in table range as promised by the header.
- Table layout must match the header's 3-D/4-D string-array convention exactly.

Filesystem relevance: none. This is color interpolation math.
