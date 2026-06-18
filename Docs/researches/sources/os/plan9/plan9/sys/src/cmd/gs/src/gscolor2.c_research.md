# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor2.c

## Purpose
Level 2 color operators and Indexed color-space implementation.

## Key Behavior
- Implements `gs_setcolorspace`, `gs_currentcolorspace`, `gs_setcolor`, and `gs_currentcolor`.
- Handles color-space reference counts, install hooks, overprint refresh, color initialization, and device-color invalidation.
- Defines the `Indexed` color-space type descriptor.
- Implements Indexed base-space forwarding for install, overprint, concrete space, and reference adjustment.
- Allocates and frees indexed maps with cached float values.
- Provides default palette lookup functions for 1, 3, 4, and N component base spaces.
- Builds Indexed spaces from either a byte lookup table or an allocated procedure-backed palette.
- Implements Indexed color restriction, lookup, concretization, serialization, and high-level `gs_includecolorspace`.

## Important Details
- `gs_setcolorspace` restores the old color space if installation or overprint update fails.
- Indexed byte-table lookup scales table bytes to floats in `[0..1]`.
- Procedure-backed Indexed spaces use `gs_indexed_map` and can replace the lookup function.
- Serialization writes the base space, hival, `use_proc`, and either map values or raw table data.

## Dependencies
Uses color-space internals, parameter/stream serialization, pattern/high-level device hooks, and Indexed-map GC descriptors.

## Research Notes
`gs_cspace_indexed_value_array` appears inverted relative to its comment and `gscindex.h`: it returns `0` when `use_proc` is true, but then returns `lookup.map->values` in the non-procedure case where `lookup.table` is the active union member. That looks like a bug in this snapshot.
