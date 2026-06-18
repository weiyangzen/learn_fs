# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/off_bitmap.h

This small header provides a typed wrapper around `xbitmap64` for file offsets.

It defines:
- `struct xoff_bitmap`, containing an `xbitmap64`.
- `xoff_bitmap_init`
- `xoff_bitmap_destroy`
- `xoff_bitmap_set`
- `xoff_bitmap_walk`

The purpose is type clarity: callers use `xfs_fileoff_t` and `xfs_filblks_t` instead of raw 64-bit bitmap coordinates. There is no independent policy or algorithm here; all behavior delegates to the generic 64-bit bitmap implementation.
