# File Research: sources/os/linux/linux/fs/xfs/xfs_aops.c

Defines XFS address-space operations and writeback/read I/O integration with iomap, reflink COW, unwritten extent conversion, DAX, zoned storage, and swapfile activation.

Key elements:
- `xfs_setfilesize` transactionally advances `i_disk_size` after successful append writeback.
- `xfs_end_ioend_write` handles write completion: shutdown/error paths, COW cleanup on failure, zoned completion, reflink COW finish, unwritten conversion, and append size update.
- `xfs_end_io` drains inode ioend lists, sorts/merges ioends, and completes reads/writes via workqueue context.
- `xfs_end_bio` records zone append locations when needed and queues ioend completion work.
- `xfs_discard_folio` punches stale delalloc mappings after writeback mapping failure.
- `xfs_map_blocks` validates or refreshes writeback iomaps, handles COW-vs-data fork precedence, converts delalloc extents to real blocks, and trims mappings at COW boundaries.
- `xfs_writeback_range` and `xfs_writeback_submit` connect XFS mapping/conversion rules to `iomap_writepages`.
- Zoned writeback uses `xfs_zoned_map_blocks`, `xfs_zoned_writeback_range`, and `xfs_zoned_writeback_submit` to consume COW-fork delalloc reservations and allocate zones at bio submission time.
- `xfs_vm_writepages` selects normal or zoned writeback; `xfs_dax_writepages` uses DAX writeback.
- `xfs_vm_bmap` refuses swap-style bmap on COW or realtime files and otherwise delegates to iomap.
- Read paths use iomap read ops, with special ioend-backed read completion when the block device has integrity checksums.
- `xfs_vm_swap_activate` rejects zoned inodes, flushes inodegc to settle reflink removals, sets the swap block device, and delegates to `iomap_swapfile_activate`.
- Exports `xfs_address_space_operations` and `xfs_dax_aops`.

Dependencies:
- Heavy use of iomap read/writeback APIs.
- Calls XFS bmap, iomap, reflink, zoned allocation, realtime group, inodegc, and transaction helpers.
- Uses workqueue completion through `m_unwritten_workqueue`.

Research notes:
- Writeback mapping validity is guarded by fork sequence numbers plus page locking assumptions.
- COW writeback always takes precedence over overlapping data-fork mappings.
- Error handling for shared writeback must cancel COW and punch data-fork delalloc to avoid stale accounting.
- Zoned writeback differs substantially: allocation is deferred until bio submission and uses anonymous writes.
- `->bmap` intentionally refuses reflink/realtime files because swap bypasses filesystem I/O paths.
