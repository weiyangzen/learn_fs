# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rmap_repair.c

## Purpose
Rebuilds per-AG reverse mapping btrees. This is the most complex AG repair path because it reconstructs ownership from primary metadata and all inodes while maintaining correctness against live filesystem updates.

## Major Components
- `struct xrep_rmap`: repair state with new-btree staging, in-memory rmapbt, live update hook, inode scanner, and counters.
- Setup:
  - `xrep_setup_ag_rmapbt`
  - `xrep_rmap_setup_scan`
  - `xrep_rmap_teardown`
- Record generation:
  - `xrep_rmap_find_rmaps`
  - `xrep_rmap_scan_inode`
  - `xrep_rmap_scan_ifork`
  - `xrep_rmap_scan_bmbt`
  - `xrep_rmap_scan_iext`
  - `xrep_rmap_find_inode_rmaps`
  - `xrep_rmap_find_refcount_rmaps`
  - `xrep_rmap_find_agheader_rmaps`
  - `xrep_rmap_find_log_rmaps`
- Space reservation and free-space metadata rmaps:
  - `xrep_rmap_reserve_space`
  - `xrep_rmap_try_reserve`
- Tree replacement:
  - `xrep_rmap_build_new_tree`
  - `xrep_rmap_get_records`
  - `xrep_rmap_reset_counters`
- Old tree reaping:
  - `xrep_rmap_remove_old_tree`
- Live updates:
  - `xrep_rmapbt_live_update`
  - `xrep_rmapbt_want_live_update`

## Control Flow and Invariants
Repair enables the rmap filesystem gate and creates an in-memory rmapbt. It first records non-free-space metadata while AG headers are locked, then cancels the transaction, unlocks AG headers, and scans filesystem inodes with an empty transaction.

The inode scan records:
- data and attr fork extents in the target AG;
- bmbt blocks through a bitmap;
- metadata btree inode blocks for realtime metadata;
- inode chunks and inode btree blocks;
- CoW staging extents and refcountbt blocks;
- AG headers and internal log.

A live rmap hook updates the in-memory btree for metadata already scanned or globally relevant while the AG lock is dropped. If live updates fail, the scan aborts and repair fails.

The new rmapbt reservation is iterative because allocating new rmapbt blocks changes free-space btree shapes and therefore the `OWN_AG` rmap records needed. After convergence, the code bulk-loads the new btree, commits it to the AGF, recalculates AGF counters, commits reservation accounting, rolls the transaction, and reaps old rmapbt blocks by finding gaps in the new rmap set minus bnobt free space.

## Dependencies and Integration
Uses:
- `xfbtree` in-memory btree support.
- `xchk_iscan` for inode scanning and visited tracking.
- `xfs_rmap_hook` for live update capture.
- `xrep_newbt` for staging.
- `xagb_bitmap` for metadata and gap tracking.
- `xrep_reap_agblocks` for old-tree cleanup.
- Common repair transaction and AG cursor helpers.

## Risk and Edge Cases
- Requires filesystem gating to block incompatible activity and prevent stale reconstruction.
- Rebuild depends on all relevant inode forks and metadata structures being readable enough to derive rmaps.
- The custom allocator uses `XFS_ALLOC_FLAG_NORMAP` to prevent recursive rmap updates while building the rmapbt itself.
- Alternate in-core rmapbt height avoids verifier failures during replacement.
