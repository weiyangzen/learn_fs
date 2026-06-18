# File Research: sources/os/linux/linux/fs/ntfs/bitmap.h

Declares NTFS bitmap helpers and provides inline convenience wrappers for bit and run updates.

Exports:
- `ntfs_trim_fs()` for FITRIM/discard support.
- `__ntfs_bitmap_set_bits_in_run()` for internal bitmap mutation with rollback mode.
- `ntfs_bitmap_set_bits_in_run()` public wrapper with rollback disabled.
- `ntfs_bitmap_set_run()`, `ntfs_bitmap_clear_run()`, `ntfs_bitmap_set_bit()`, and `ntfs_bitmap_clear_bit()` convenience helpers.

Core mechanics:
- All wrappers reduce to `__ntfs_bitmap_set_bits_in_run()` with `value` set to either 1 or 0.
- The API operates on a VFS inode representing a bitmap attribute.

Notable risks:
- The inline wrappers do no validation; all validation and rollback behavior is centralized in `bitmap.c`.
