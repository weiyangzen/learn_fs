# File Research: sources/os/linux/linux-stable/fs/ntfs/mft.c

`mft.c` implements NTFS master file table record handling: mapping records from `$MFT`, validating and MST-fixing them, allocating/freeing records, extending `$MFT` and `$MFT/$BITMAP`, syncing `$MFTMirr`, and writing dirty MFT folios.

Key responsibilities:
- `ntfs_mft_record_check()` validates FILE magic, update sequence array placement/count, allocation size, in-use size, and attribute offset safety.
- `map_mft_record()` and `map_mft_record_folio()` pin the `$MFT` folio, copy the target record into `ni->mrec`, apply `post_read_mst_fixup()`, and validate the result.
- `map_extent_mft_record()` loads or creates an extent `ntfs_inode`, verifies the MFT reference sequence number, and attaches it to the base inode’s extent array.
- `mark_mft_record_dirty()` support is completed by `__mark_mft_record_dirty()`, which marks the base VFS inode `I_DIRTY_DATASYNC`.
- `write_mft_record_nolock()` writes one mapped record through bios, applying `pre_write_mst_fixup()` to the folio copy and syncing `$MFTMirr` for mirrored record numbers.
- `ntfs_may_write_mft_record()` decides whether writeback may write a record directly from the `$MFT` page cache or must defer to the owning inode path to avoid lock/order races.
- `ntfs_mft_bitmap_find_and_alloc_free_rec_nolock()` scans `$MFT/$BITMAP`, skipping reserved records below 64 except special `$MFT` extension allocation logic.
- `ntfs_mft_bitmap_extend_allocation_nolock()` and `ntfs_mft_bitmap_extend_initialized_nolock()` grow bitmap allocation and initialized/data size, with rollback paths for cluster/runlist/mapping-pair changes.
- `ntfs_mft_data_extend_allocation_nolock()` extends `$MFT/$DATA`, allocates clusters in the MFT zone, merges runlists, updates mapping pairs, and rolls back on failures.
- `ntfs_mft_record_layout()` formats an unused record header and terminating attribute.
- `ntfs_mft_record_format()` writes a formatted record into the `$MFT` page cache and marks the folio dirty.
- `ntfs_mft_record_alloc()` coordinates bitmap allocation, `$MFT` extension/initialization, record formatting, inode setup, base-vs-extent behavior, and rollback.
- `ntfs_mft_record_free()` marks a record unused, advances its sequence number, writes it, clears the bitmap bit, and rolls back if bitmap cleanup fails.
- `ntfs_mft_writepages()` iterates dirty `$MFT` folios and delegates each to `ntfs_write_mft_block()`.
- `ntfs_write_mft_block()` writes eligible MFT records from a folio, handles cluster-size splits, builds bios, syncs mirror records, and defers `iput()` until after the folio lock is released.

Important data/control flow:
- Mapped record access is copy-based: `ni->mrec` is an allocated fixed-up copy; `ni->folio` pins the backing folio.
- Writeout copies `ni->mrec` back into the folio, applies MST protection there, then submits block I/O.
- `$MFT` allocation is tied to `$MFT/$BITMAP`: the bitmap bit is set before the record is made externally reachable, and rollback clears it if later steps fail.
- `$MFTMirr` is synchronously updated for record numbers below `vol->mftmirr_size`.

Locking and safety notes:
- Allocation uses `vol->mftbmp_lock`, `$MFT` `mrec_lock`, runlist locks, and `memalloc_nofs_save()` to avoid filesystem recursion.
- Extent inode arrays are protected by `base_ni->extent_lock`.
- Writeback avoids lock inversion by using `find_inode_nowait()`, `mutex_trylock()`, and deferred inode reference dropping.
- Many metadata mutation paths call `NVolSetErrors()` if rollback cannot fully restore consistency.

Dependencies:
- MST helpers from `mst.c`.
- Runlist and mapping-pair helpers from `runlist.c`.
- Bitmap/cluster allocation helpers from `bitmap.h` and `lcnalloc.h`.
- Attribute lookup/update helpers used when modifying `$MFT` and `$MFT/$BITMAP` attribute records.
