# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/fsb_bitmap.h

This header provides a type-specific wrapper around `xbitmap64` for filesystem block numbers.

Key definition:
- `struct xfsb_bitmap` contains an `xbitmap64 fsbitmap`.

Provided helpers:
- `xfsb_bitmap_init`
- `xfsb_bitmap_destroy`
- `xfsb_bitmap_set`
- `xfsb_bitmap_walk`

Purpose and integration:
- The wrapper makes bitmap use type-aware for `xfs_fsblock_t` ranges and `xfs_filblks_t` lengths.
- It delegates all storage and walking behavior to the generic 64-bit bitmap implementation.
