# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/ino_bitmap.h

This header provides a type-specific wrapper around `xbitmap64` for inode numbers.

Key definition:
- `struct xino_bitmap` contains an `xbitmap64 inobitmap`.

Provided helpers:
- `xino_bitmap_init`
- `xino_bitmap_destroy`
- `xino_bitmap_set`
- `xino_bitmap_test`

Purpose:
- Stores individual `xfs_ino_t` values in a 64-bit bitmap abstraction.
- `xino_bitmap_set` records one inode at a time.
- `xino_bitmap_test` checks whether one inode is present by testing a length-one range.
