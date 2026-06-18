# File Research: sources/os/linux/linux/fs/ntfs/mft.c

Core NTFS MFT record management: validates, maps, writes, allocates, frees, mirrors, and writebacks MFT records.

Key responsibilities:
- Validates MFT record structure in `ntfs_mft_record_check()`: `FILE` magic, USA/fixup fields, allocation size, in-use size, and attribute offset bounds.
- Maps records through `$MFT` page cache with `map_mft_record()` and `map_mft_record_folio()`, copying record bytes into `ni->mrec`, applying `post_read_mst_fixup()`, and retaining the source folio and offset.
- Handles extent records via `map_extent_mft_record()`, including base inode reference management, extent cache lookup, sequence validation, and dynamic `extent_ntfs_inos` growth.
- Marks MFT metadata dirty through `__mark_mft_record_dirty()` and base VFS inode `I_DIRTY_DATASYNC`.
- Writes records with MST protection in `write_mft_record_nolock()` and updates `$MFTMirr` for mirrored records via `ntfs_sync_mft_mirror()`.
- Controls page-cache writeback of `$MFT` folios in `ntfs_mft_writepages()` and `ntfs_write_mft_block()`.

Allocation and growth:
- `ntfs_mft_bitmap_find_and_alloc_free_rec_nolock()` scans `$MFT/$BITMAP`, skipping records below `RESERVED_MFT_RECORDS` except special `$MFT` extension behavior.
- `ntfs_mft_bitmap_extend_allocation_nolock()` grows bitmap allocation by appending or allocating a cluster, then rebuilds mapping pairs and rolls back on failure.
- `ntfs_mft_bitmap_extend_initialized_nolock()` extends initialized bitmap bytes by 8 and zeros them.
- `ntfs_mft_data_extend_allocation_nolock()` extends `$MFT/$DATA`, updates runlists and mapping pairs, and rolls back allocated clusters if metadata updates fail.
- `ntfs_mft_record_layout()` formats an empty record with valid USA, attributes offset, `AT_END`, sequence number, and NTFS 3.1 record number when applicable.
- `ntfs_mft_record_alloc()` orchestrates bitmap allocation, `$MFT` growth, record formatting, inode setup, extent attachment, dirtying, rollback, and free-record accounting.
- `ntfs_mft_record_free()` clears `MFT_RECORD_IN_USE`, bumps sequence number, writes the record, clears the bitmap bit, and rolls back where possible.

Concurrency and writeback:
- Uses `mrec_lock`, `extent_lock`, `mftbmp_lock`, runlist locks, and `lcnbmp_lock`; several paths explicitly preserve lock ordering.
- `ntfs_may_write_mft_record()` avoids deadlocks during folio writeback by checking inode cache state, dirty state, deletion/creation state, and trying mrec locks without blocking.
- Deferred `iput()` handling avoids dropping inode refs while holding folio locks.
- Async BIO writes retain folios through `ntfs_bio_end_io()` to prevent eviction while I/O is in flight.

Failure behavior:
- Sets `NVolErrors()` when rollback or write failures can leave metadata inconsistent.
- Converts stale extent/base sequence references to `-EIO`.
- Leaves dirty records dirty or redirties on retryable write failures.
- Enforces the 2^32 MFT-record limit.

Important dependencies:
- MST helpers from `mst.c`.
- Bitmap operations from `bitmap.h`.
- Cluster allocation/free from `lcnalloc.h`.
- Attribute lookup, resizing, mapping pairs, and runlist manipulation.
- Folio, BIO, iomap, and writeback kernel APIs.
