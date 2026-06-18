# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/bmap_repair.c

## Purpose
Repairs inode data or attr fork block mappings by reconstructing bmap records from reverse mappings, preserving delalloc reservations, rebuilding the incore and optional ondisk bmbt fork, resetting inode block counters/quota, and reaping old bmbt blocks.

## Main Entry Points
- `xrep_bmap`: generic data/attr fork repair.
- `xrep_bmap_data`: data fork repair, allowing unwritten extents.
- `xrep_bmap_attr`: attr fork repair, rejecting unwritten extents.

## Key Behavior
Repair requires rmapbt. It scans realtime rmaps where relevant and all data-device AG rmaps, collecting records owned by the target inode. It accounts all inode-owned blocks for `i_nblocks`, but only converts rmaps for the selected fork into bmap records. BMBT block rmaps are recorded into `old_bmbt_blocks` for later reaping. Data fork delalloc reservations from the old incore extent tree are appended so repair does not lose pending allocations.

Each rmap is checked for obvious conflicts: valid AG/rtgroup range, valid file offset, no contradictory flags, not free space, not inode chunks, and realtime/data-device placement rules. Reconstructed mappings are split at `XFS_MAX_BMBT_EXTLEN`, converted to disk bmbt records, and sorted by file offset with overlap detection.

`xrep_bmap_build_new_fork` creates a staged fork via `xrep_newbt_init_inode`. If the number of real mappings fits in extents format, it loads an incore extent fork. Otherwise it computes btree geometry, reserves transaction space and new btree blocks, bulk-loads a staged bmbt, and loads the incore extent tree. It then commits the staged fork to the inode, updates `i_nblocks`, adjusts quota by the bmbt block delta, commits newbt reservations, rolls the transaction, and reaps old bmbt blocks.

For reflink filesystems, repair preserves an existing reflink inode flag and can discover shared extents while rebuilding a regular file data fork; if shared extents are found, it sets `XFS_DIFLAG2_REFLINK`.

## Dependencies and Interactions
Uses rmapbt/rtrmapbt, refcount, realtime groups, quota, bmbt staging, `xrep_newbt`, fsblock bitmap wrappers, `xfarray`, and reaping helpers. It assumes higher-level repair handles local/dev/uuid/meta-btree fork formats.

## Failure Handling
Unsupported without rmapbt. Non-repairable fork formats return no work or corruption depending on format. All newbt state is canceled on failure, old block bitmap and mapping arrays are destroyed, and old bmbt blocks are reaped only after the new fork is committed.
