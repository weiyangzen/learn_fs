# File Research: sources/os/linux/linux/fs/xfs/scrub/dab_bitmap.h

## Role
Defines a type-checked bitmap wrapper for directory/attribute block numbers (`xfs_dablk_t`).

## Interfaces
- `struct xdab_bitmap`: wraps `struct xbitmap32`.
- `xdab_bitmap_init`, `xdab_bitmap_destroy`: lifecycle helpers.
- `xdab_bitmap_set`: records a DA block range.
- `xdab_bitmap_test`: tests for a DA block range and returns its length.

## Dependencies
Uses the generic 32-bit bitmap API (`xbitmap32`) while preserving DA-block-specific call sites.

## Notes
This is intentionally thin; its value is type clarity and preventing accidental mixing of DA block numbers with other block-number domains.
