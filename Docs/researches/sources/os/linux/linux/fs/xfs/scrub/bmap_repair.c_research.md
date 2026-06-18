# File Research: sources/os/linux/linux/fs/xfs/scrub/bmap_repair.c

This file repairs inode data and attr fork block mappings by reconstructing the fork from reverse mapping records. It gathers all rmaps owned by the inode and relevant fork, stages a new extent list or bmap btree, swaps the staged fork into the inode, updates counters and quotas, and reaps old bmbt blocks.

`struct xrep_bmap` tracks old bmbt blocks in an `xfsb_bitmap`, a staged `xrep_newbt`, recovered bmap records in an `xfarray`, total file-owned blocks, old bmbt block count, real mapping count, target fork, reflink scan state, and whether unwritten extents are permitted. Data fork repair permits unwritten extents; attr fork repair does not.

Rmap scanning walks realtime groups when applicable and all AGs on the data device. For each matching inode owner, the code validates that records are physically within the group, logically valid, not free space, not inode chunks, and not contradictory in flags. It records all file-owned blocks for later `i_nblocks` reconstruction, records old bmbt blocks separately, filters to the requested fork, and converts data records into one or more bmbt records capped at `XFS_MAX_BMBT_EXTLEN`. Existing delalloc reservations from the incore extent tree are preserved for eligible forks.

For reflink filesystems, repair preserves an existing reflink inode flag and can discover shared data extents via refcount btree lookup to set `XFS_DIFLAG2_REFLINK` when rebuilding a regular file that was missing the flag. Recovered records are sorted by file offset and checked for overlap.

Rebuild chooses extents format when the real mapping count fits the fork, otherwise bulk-loads a new bmap btree. It initializes a staged inode fork, reserves blocks for btree format with quota override, loads real mappings into the btree and all mappings including delalloc into the incore extent tree, commits the staged fork, recalculates `i_nblocks` by combining rmap-discovered file blocks with the delta in bmbt block count, adjusts quota block counts, commits newbt reservations, rolls the transaction, and reaps old bmbt blocks with the inode bmbt owner info.

`xrep_bmap_check_inputs` requires rmapbt support, ignores nonexistent or local/device/UUID/meta-btree forks, and validates that only files, symlinks, and directories receive data fork repair. Entry points are `xrep_bmap_data` and `xrep_bmap_attr`.
