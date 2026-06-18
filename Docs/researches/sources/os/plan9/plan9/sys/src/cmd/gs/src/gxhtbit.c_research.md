# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhtbit.c

Purpose: builds and updates halftone order bit representations from threshold arrays.

Order construction:
- `construct_ht_order_default`: fills `gx_ht_bit.mask` values from thresholds and calls `gx_ht_complete_threshold_order`.
- `construct_ht_order_short`: builds compact ushort bit-index arrays and level offsets from threshold values.
- Short construction also checks registered predefined halftone resources; if a match is found, it frees allocated arrays and points the order at built-in constant data.

Coordinate lookup:
- `ht_bit_index_default`: converts a default `gx_ht_bit` entry to x/y bit coordinates by locating the mask bit.
- `ht_bit_index_short`: converts compact ushort bit index to x/y coordinates using raster width.

Rendering:
- `render_ht_default`: toggles bits between old and new levels using `gx_ht_bit.offset/mask`.
- `render_ht_short`: toggles bits between old and new levels using compact bit indexes.
- Both renderers handle level movement up or down with unrolled switch logic and XOR bit inversion.

Exported table:
- `ht_order_procs_table[2]` maps order representation to element size, construction, index lookup, and render functions.

Dependencies:
- Uses bitmap raster math, halftone tile definitions, transfer maps, and device halftone resource lists.

Research notes:
- Threshold values are clamped to at least 1 before use.
- Compact representation accounts for bitmap row padding when computing stored bit indexes.
