# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rtb_bitmap.h

## Purpose
Provides a type-specific wrapper around `xbitmap64` for absolute realtime block numbers, `xfs_rtblock_t`.

## Major Components
- `struct xrtb_bitmap`: contains an `xbitmap64`.
- Inline helpers:
  - `xrtb_bitmap_init`
  - `xrtb_bitmap_destroy`
  - `xrtb_bitmap_set`
  - `xrtb_bitmap_walk`

## Control Flow and Invariants
All behavior delegates to the generic 64-bit bitmap, preserving realtime block type clarity at call sites.

## Dependencies and Integration
Available to realtime scrub/repair code that needs absolute realtime block range tracking.

## Risk and Edge Cases
No range validation is added in this wrapper; callers must provide valid realtime block ranges.
