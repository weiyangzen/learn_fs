# File Research: sources/os/linux/linux/fs/xfs/scrub/ino_bitmap.h

Provides a typed single-inode bitmap wrapper around the generic 64-bit bitmap.

Main API:
- `struct xino_bitmap` embeds `struct xbitmap64`.
- `xino_bitmap_init` and `xino_bitmap_destroy` manage lifetime.
- `xino_bitmap_set` records one `xfs_ino_t`.
- `xino_bitmap_test` tests whether one inode number is present.

This is used where scrub/repair needs sparse tracking of individual filesystem inode numbers without exposing raw 64-bit bitmap calls.
