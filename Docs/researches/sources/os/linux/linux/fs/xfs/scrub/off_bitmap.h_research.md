# File Research: sources/os/linux/linux/fs/xfs/scrub/off_bitmap.h

## Role
Provides a type-checked wrapper around `xbitmap64` for `xfs_fileoff_t` file offsets.

## API
- `xoff_bitmap_init` initializes the wrapped bitmap.
- `xoff_bitmap_destroy` releases bitmap storage.
- `xoff_bitmap_set` marks a file-offset range.
- `xoff_bitmap_walk` iterates marked ranges using an `xbitmap64` callback.

## Integration
This is a small helper header for scrub/repair code that wants bitmap operations expressed in XFS file-offset units instead of raw 64-bit integers.
