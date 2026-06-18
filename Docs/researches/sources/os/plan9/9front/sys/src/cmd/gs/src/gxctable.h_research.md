# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxctable.h

Interface for 3-D and 4-D color lookup tables.

Key contents:
- Defines `gx_color_lookup_table` with dimension count, dimensions, output component count, and table string array.
- Documents table layout for 3-D and 4-D tables.
- Declares `gx_color_interpolate_nearest` and `gx_color_interpolate_linear`.
- Inputs are fixed-point table indices; outputs are fraction color values.

Notable dependencies:
- Fixed-point and fraction definitions.

Research notes:
- 4-D tables are stored as an array indexed by the first two dimensions, each entry containing the remaining dimensions and output components.
- String sizes are retained largely to simplify garbage collection.
