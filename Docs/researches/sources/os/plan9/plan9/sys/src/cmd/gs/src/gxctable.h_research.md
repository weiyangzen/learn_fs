# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxctable.h

## Purpose
Declares the color lookup table data model and interpolation APIs.

## Public Surface
- `gx_color_lookup_table`: describes a 3-D or 4-D table with dimension count, dimensions, output component count, and array of constant strings.
- `gx_color_interpolate_nearest(...)`: nearest-sample lookup.
- `gx_color_interpolate_linear(...)`: trilinear/4-D interpolated lookup.

## Semantics
- For 3-D tables, `table[i]` points to data of length `dims[1] * dims[2] * m`.
- For 4-D tables, `table[i]` spans the first two dimensions as `dims[0] * dims[1]` strings of length `dims[2] * dims[3] * m`.
- Input fixed-point indices are guaranteed by callers to be within `[0, dims[n]-1]`.

## Dependencies
Includes fixed-point and fraction types.

## Risks and Notes
- String sizes are retained mostly to simplify garbage collection even though table slices are uniform.

Filesystem relevance: none. This is a rendering math interface.
