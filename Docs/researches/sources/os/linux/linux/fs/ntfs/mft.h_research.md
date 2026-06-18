# File Research: sources/os/linux/linux/fs/ntfs/mft.h

Public MFT API header for NTFS.

Exports:
- Record mapping: `map_mft_record()`, `unmap_mft_record()`, `map_extent_mft_record()`, `unmap_extent_mft_record()`.
- Dirtying: `__mark_mft_record_dirty()` and inline `mark_mft_record_dirty()`, which only calls the heavy path when the inode was not already marked dirty.
- Write helpers: `ntfs_sync_mft_mirror()`, `write_mft_record_nolock()`, inline `write_mft_record()`.
- Allocation/free/check/writeback: `ntfs_mft_record_alloc()`, `ntfs_mft_record_free()`, `ntfs_mft_record_check()`, `ntfs_mft_writepages()`, `ntfs_mft_mark_dirty()`.
- Declares `ntfs_mft_records_write()`, though that implementation is not in the grouped `mft.c`.

Notable behavior:
- Inline `write_mft_record()` locks the containing folio around `write_mft_record_nolock()` to serialize inode writeback and page-cache writeback paths.
- Header depends on `inode.h`, highmem, and pagemap types.
