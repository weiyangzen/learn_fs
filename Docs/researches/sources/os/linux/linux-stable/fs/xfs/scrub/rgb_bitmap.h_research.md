# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rgb_bitmap.h

## Purpose
Provides a type-specific wrapper around `xbitmap32` for realtime-group block numbers, `xfs_rgblock_t`.

## Major Components
- `struct xrgb_bitmap`: contains an `xbitmap32`.
- Inline helpers:
  - `xrgb_bitmap_init`
  - `xrgb_bitmap_destroy`
  - `xrgb_bitmap_set`
  - `xrgb_bitmap_walk`

## Control Flow and Invariants
The wrapper preserves type intent for rtgroup-relative block bitmaps while delegating storage and traversal to the generic 32-bit bitmap implementation.

## Dependencies and Integration
Used by realtime rmap repair to collect rtgroup-relative extents, notably CoW staging extents and generated rtrmap records.

## Risk and Edge Cases
There is no extra validation beyond the underlying `xbitmap32`; callers must pass valid `xfs_rgblock_t` ranges.
