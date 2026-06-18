# File Research: sources/os/linux/linux/fs/xfs/scrub/rtrmap_repair.c

## Purpose
Rebuilds realtime reverse mapping btrees. It scans realtime file mappings and CoW staging extents, records old rtrmapbt blocks from data-device rmapbts, bulk-loads a new metadata-inode rtrmapbt, and reaps the old tree.

## Major Components
- `struct xrep_rtrmap`: repair state with in-memory rtrmapbt, new-btree staging, old block bitmap, live update hook, inode scan, and counters.
- Setup/teardown:
  - `xrep_setup_rtrmapbt`
  - `xrep_rtrmap_setup_scan`
  - `xrep_rtrmap_teardown`
- Record collection:
  - `xrep_rtrmap_find_rmaps`
  - `xrep_rtrmap_scan_inode`
  - `xrep_rtrmap_scan_dfork`
  - `xrep_rtrmap_scan_bmbt`
  - `xrep_rtrmap_scan_iext`
  - `xrep_rtrmap_find_refcount_rmaps`
  - `xrep_rtrmap_scan_ag`
- Tree build:
  - `xrep_rtrmap_build_new_tree`
  - `xrep_rtrmap_get_records`
  - `xrep_rtrmap_iroot_size`
- Live update hook:
  - `xrep_rtrmapbt_live_update`
  - `xrep_rtrmapbt_want_live_update`
- Top-level repair: `xrep_rtrmapbt`.

## Control Flow and Invariants
Repair fixes metadata inode forks, initializes an in-memory rtrmapbt and old-block bitmap, then:
- Records rt superblock ownership for rtgroup 0 if present.
- Records realtime CoW staging extents from rtrefcountbt.
- Unlocks rt metadata and scans inodes using an empty transaction.
- For realtime files, records data fork mappings in the target rtgroup, coalescing adjacent compatible extents.
- Re-locks rtgroup metadata, scans all AG rmapbts for old rtrmapbt inode blocks, and counts/validates generated records.
- Builds a new metadata-inode btree, reserves inode blocks, bulk-loads from the in-memory rtrmapbt, commits the staged tree, updates inode block count, rolls the transaction, and reaps old btree blocks.

Live rtrmap updates are captured through an rmap hook while the inode scan is running. Updates for non-inode owners are always wanted because CoW staging extents were scanned before the iscan.

## Dependencies and Integration
Uses:
- `xfbtree` in-memory rtrmapbt.
- `xchk_iscan`.
- `xfs_rmap_hook`.
- `xrgb_bitmap` for rtgroup-relative CoW extent collection.
- `xfsb_bitmap` for old data-device metadata blocks.
- metadata-inode newbt helpers and reap helpers.

## Risk and Edge Cases
- Repair assumes realtime rmap reconstruction only needs realtime file data fork mappings plus CoW staging and rt superblock metadata.
- Old rtrmapbt blocks are not on the realtime device; they are data-device blocks owned by the rtrmap metadata inode and found via all AG rmapbts.
- A failed live update aborts the scan and causes repair failure to avoid installing stale metadata.
