# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rtrefcount_repair.c

## Purpose
Rebuilds a realtime refcount btree from realtime reverse mappings. It constructs shared and CoW refcount records, stages a new metadata-inode btree, commits it into the rtrefcount inode, and reaps old rtrefcountbt blocks.

## Major Components
- `struct xrep_rtrefc`: repair state with generated records, new-btree state, old block bitmap, and cursor position.
- `xrep_setup_rtrefcountbt`: sets up xfbtree backing storage.
- `xrep_rtrefc_find_refcounts`: scans old metadata blocks and performs sweep-line overlap accounting over rtrmapbt.
- `xrep_rtrefc_stash` / `xrep_rtrefc_stash_cow`: validate and store generated records.
- `xrep_rtrefc_scan_ag`: scans data-device rmapbt for blocks owned by the rtrefcount inode.
- `xrep_rtrefc_build_new_tree`: bulk-loads and commits a staged metadata-inode btree.
- `xrep_rtrefcountbt`: top-level repair.

## Control Flow and Invariants
Repair requires rtrmapbt. It first repairs metadata inode forks, then:
- Scans every AG rmapbt for old blocks owned by the rtrefcount inode.
- Walks realtime rmaps to derive shared and CoW refcount records.
- Rejects sb metadata inode owners, attr fork records, bmbt blocks, and invalid realtime refcount extents.
- Ensures refcount records are full realtime extent aligned and in-use.
- Sorts records in ondisk order.
- Builds the new btree with `xrep_newbt_init_metadir_inode`, reserves inode blocks, bulk-loads, commits the staged rtrefcountbt, updates `i_nblocks`, commits newbt accounting, rolls transaction, and reaps old blocks.

## Dependencies and Integration
Uses `rcbag`, `xfarray`, `xfsb_bitmap`, metadata inode repair helpers, rtgroup btree cursors, AG rmap scanning, and `xrep_reap_metadir_fsblocks`.

## Risk and Edge Cases
- The generated record array is sized for one record per realtime extent.
- Rebuild fails if rtrmapbt is unavailable.
- Old rtrefcountbt blocks live on the data device as metadata inode btree blocks, so the repair scans all AG rmapbts to find them.
