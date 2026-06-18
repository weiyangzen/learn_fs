# File Research: sources/os/linux/linux-stable/fs/ntfs/mft.h

`mft.h` declares the MFT record mapping, dirtying, writeout, allocation/free, validation, and writeback interfaces used by the NTFS driver.

Key contents:
- Declares `map_mft_record()`, `unmap_mft_record()`, and `map_extent_mft_record()`.
- Provides `unmap_extent_mft_record()` as a direct wrapper over `unmap_mft_record()`.
- Defines `mark_mft_record_dirty()`, which uses `NInoTestSetDirty()` to avoid duplicate dirtying and calls `__mark_mft_record_dirty()` only on the first transition to dirty.
- Declares mirror sync and record write APIs: `ntfs_sync_mft_mirror()`, `write_mft_record_nolock()`, and inline `write_mft_record()`.
- Inline `write_mft_record()` locks the containing folio, invokes the no-lock writer, and unlocks it, serializing inode write paths against page-cache writeback.
- Declares `ntfs_mft_record_alloc()`, `ntfs_mft_record_free()`, `ntfs_mft_record_check()`, `ntfs_mft_writepages()`, and `ntfs_mft_mark_dirty()`.

Design role:
- This header is the public boundary for MFT lifecycle operations.
- It centralizes the rule that callers modifying mapped MFT records must mark them dirty before unmapping.
