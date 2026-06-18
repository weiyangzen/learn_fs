# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/dab_bitmap.h

## Role

Small type-safe bitmap wrapper for directory/attribute block numbers.

## Key Definitions

- `struct xdab_bitmap` wraps `struct xbitmap32`.
- `xdab_bitmap_init()` initializes the bitmap.
- `xdab_bitmap_destroy()` frees bitmap resources.
- `xdab_bitmap_set()` records a range of `xfs_dablk_t` values.
- `xdab_bitmap_test()` queries a directory/attribute block range.

## Research Notes

This header provides typed helpers so DA block-number bitmaps do not directly expose the generic 32-bit bitmap API.
