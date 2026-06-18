# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxctable.c

Color lookup-table interpolation implementation.

Key behavior:
- `gx_color_interpolate_nearest` selects nearest table entries for 3-D or 4-D color lookup tables and converts byte table values to `frac`.
- `interpolate_accum` performs trilinear interpolation for 3-D tables.
- For 4-D tables, interpolation is implemented as two 3-D interpolations blended along the first dimension.
- Handles boundary cells by reusing the last available sample when an index is at the maximum dimension.
- `gx_color_interpolate_linear` is the public entry point for linear interpolation.

Notable dependencies:
- Fixed-point helpers from `gxfixed.h`, fraction helpers from `gxfrac.h`, and table layout from `gxctable.h`.

Research notes:
- Table entries are byte-valued and promoted to Ghostscript fractions for output.
- The implementation assumes indices are already range-checked by the caller as documented in the header.
