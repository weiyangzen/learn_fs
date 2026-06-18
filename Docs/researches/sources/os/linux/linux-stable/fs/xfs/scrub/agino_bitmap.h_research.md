# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/agino_bitmap.h

## Purpose
Provides a type-checked per-AG inode-number bitmap wrapper around `xbitmap32`.

## API
- `struct xagino_bitmap` contains one `struct xbitmap32`.
- `xagino_bitmap_init`
- `xagino_bitmap_destroy`
- `xagino_bitmap_clear`
- `xagino_bitmap_set`
- `xagino_bitmap_test`
- `xagino_bitmap_walk`

## Notes
The wrapper prevents accidental mixing of generic 32-bit bitmap units with `xfs_agino_t` values. It is used by AGI repair to track unlinked inodes while rebuilding unlinked bucket chains.
