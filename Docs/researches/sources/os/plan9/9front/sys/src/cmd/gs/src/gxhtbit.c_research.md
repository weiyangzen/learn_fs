# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhtbit.c

## Role

`gxhtbit.c` implements halftone order construction and tile bit updating for Ghostscript's imaging library.

This is imaging/halftone infrastructure, not filesystem code.

## Main Responsibilities

- Builds standard or short halftone order representations from threshold arrays.
- Maps order indices back to bit coordinates.
- Incrementally renders halftone tiles by XOR-ing changed bits between old and new levels.
- Exports `ht_order_procs_table`, the procedure table for the supported order-data representations.

## Important Functions

- `construct_ht_order_default`: stores threshold masks in `gx_ht_bit` records and completes the threshold order.
- `construct_ht_order_short`: counts threshold values, builds compact `ushort` bit indices adjusted for bitmap row padding, and replaces dynamically allocated data with predefined built-in halftone resources when an exact match is found.
- `ht_bit_index_default` and `ht_bit_index_short`: return `(x,y)` coordinates for an order entry.
- `render_ht_default` and `render_ht_short`: update an existing tile from `old_level` to `level` by XOR-ing each bit crossed by the level delta.

## Data Representations

- Default representation uses `gx_ht_bit` with byte offset and mask.
- Short representation stores one padded bit index per threshold bit as `ushort`.
- `ht_order_procs_table[2]` binds element size, construct, index, and render procedures for both representations.

## Notable Risks

- Rendering depends on incremental XOR from the tile's current level; callers must keep `pbt->level` accurate.
- `construct_ht_order_short` mutates ownership: it may free dynamic arrays and point the order at const built-in resources while setting `data_memory = 0`.
- The switch-based render loops intentionally use fall-through for small deltas and `goto` for larger deltas; edits require care.
