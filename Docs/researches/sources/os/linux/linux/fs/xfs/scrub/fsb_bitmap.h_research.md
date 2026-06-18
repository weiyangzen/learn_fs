# File Research: sources/os/linux/linux/fs/xfs/scrub/fsb_bitmap.h

Provides a typed wrapper around the generic 64-bit scrub bitmap for filesystem block numbers.

Main API:
- `struct xfsb_bitmap` embeds `struct xbitmap64`.
- `xfsb_bitmap_init` and `xfsb_bitmap_destroy` manage bitmap lifetime.
- `xfsb_bitmap_set` records a filesystem-block range using `xfs_fsblock_t` and `xfs_filblks_t`.
- `xfsb_bitmap_walk` iterates set ranges with the generic 64-bit walk callback type.

This wrapper gives callers type-specific names for filesystem-block tracking while reusing the interval-tree bitmap implementation.
