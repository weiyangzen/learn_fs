# File Research: sources/os/linux/linux-stable/fs/ntfs/bitmap.h

Purpose: Public bitmap API and convenience wrappers.

Exports:
- `ntfs_trim_fs()`
- `__ntfs_bitmap_set_bits_in_run()`

Inline helpers:
- `ntfs_bitmap_set_bits_in_run()` wraps the internal implementation with rollback disabled.
- `ntfs_bitmap_set_run()` sets a range of bits.
- `ntfs_bitmap_clear_run()` clears a range of bits.
- `ntfs_bitmap_set_bit()` sets one bit.
- `ntfs_bitmap_clear_bit()` clears one bit.

Dependencies:
- Includes Linux fs declarations and NTFS volume definitions.
- Designed for bitmap inode callers that should not need to pass rollback state.
