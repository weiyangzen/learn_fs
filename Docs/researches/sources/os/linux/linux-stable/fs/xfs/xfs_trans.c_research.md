# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_trans.c

## Purpose
Implements core XFS transaction lifecycle and reservation handling: initialization of transaction reservation tables, allocation, reservation, commit, cancel, roll, item management, superblock delta accounting, and high-level helpers that allocate transactions for inode, inode-create, inode-change, and directory operations.

## Main APIs
- `xfs_trans_init` computes mount transaction reservations and traces them when tracepoints are enabled.
- `xfs_trans_alloc` allocates a transaction, starts freeze/write accounting, enters NOFS allocation context, reserves log space, data blocks, and realtime extents, and retries ENOSPC once after speculative blockgc flushing.
- `xfs_trans_alloc_empty` creates a no-reservation transaction for metadata lookups that need transaction buffer regrab semantics.
- `xfs_trans_mod_sb` records superblock field deltas and marks the transaction dirty or superblock-dirty as needed.
- `xfs_trans_unreserve_and_mod_sb` returns unused reservations and applies in-core superblock/per-cpu counter deltas.
- `xfs_trans_add_item` and `xfs_trans_del_item` maintain the transaction log item list.
- `xfs_trans_commit` finishes deferred work for permanent transactions and commits through `__xfs_trans_commit`.
- `xfs_trans_cancel` releases reservations/items and forces shutdown if a dirty transaction is cancelled before shutdown.
- `xfs_trans_roll` duplicates a permanent transaction, commits the old one with log ticket regrant, and reestablishes NOFS state for the new transaction.
- `xfs_trans_reserve_more` and `xfs_trans_reserve_more_inode` add block, realtime, and quota reservations to an existing transaction.
- `xfs_trans_alloc_inode`, `xfs_trans_alloc_icreate`, `xfs_trans_alloc_ichange`, and `xfs_trans_alloc_dir` compose allocation, inode locking/joining, dquot attach, quota reservation, blockgc retry, and fallback reservation behavior for common metadata operations.

## Key Behavior
Transaction allocation is split between `__xfs_trans_alloc` and `xfs_trans_reserve`. The former allocates the object, starts internal write accounting unless `XFS_TRANS_NO_WRITECOUNT` is set, enters `memalloc_nofs`, initializes item/defer/busy lists, and records mount state. The latter reserves free data blocks, log ticket space, permanent log reservation flags, and realtime extents.

Permanent transaction rolling uses `xfs_trans_dup` to move remaining block/realtime reservations, duplicate quota accounting, move deferred operations, and share the log ticket. The old transaction is then committed with regrant; the new transaction keeps the log reservation chain alive.

Commit processing first applies superblock and dquot deltas, sorts dirty log items by item-specific sort keys to avoid precommit lock ordering deadlocks, runs precommit callbacks, and either unreserves clean transactions or submits dirty transactions to the CIL. Synchronous transactions force the committed CIL sequence to disk.

Cancel processing treats dirty cancellation as an in-core corruption condition unless shutdown is already underway. Deferred ops attached to a cancelled permanent transaction are also treated as dirty, cancelled explicitly, and cause shutdown.

## Superblock Accounting
`xfs_trans_mod_sb` accumulates deltas for inode counts, free inode counts, free data blocks, reserved-on-disk block updates, free realtime extents, reserved realtime extent updates, filesystem size geometry, AG count, imax percentage, realtime geometry, realtime group count, and related superblock fields.

`xfs_trans_apply_sb_deltas` logs changes to the superblock buffer on commit. It handles lazy sbcount filesystems, rtgroups, older realtime frextents requirements, target device sector counts, recomputation of realtime group block log when extent size changes, and whole-superblock logging for noncontiguous geometry updates.

`xfs_trans_unreserve_and_mod_sb` returns unused reservations to free counters and applies in-core deltas, with special handling for lazy counters and realtime group behavior.

## Dependencies
Depends on XFS mount state, log tickets/CIL, transaction reservation calculations, quota/dquot accounting, deferred operations, inode locking and dquot attachment, blockgc, realtime bitmap/group helpers, busy extent tracking, superblock helpers, tracepoints, and shutdown/error infrastructure.

## Failure Handling
- Reservation failure unwinds blocks, log tickets, and realtime extents.
- Initial ENOSPC allocation may retry after blockgc flushing.
- Quota failures in inode helpers may retry after quota blockgc.
- Precommit errors force filesystem shutdown because dirty transaction state cannot be safely recovered in memory.
- Dirty transaction cancellation forces shutdown to prevent inconsistent dirty metadata from reaching disk.
- `xfs_trans_reserve_more_inode` rolls back incremental block/realtime reservations if quota reservation fails.

## Risk Notes
This file is correctness-critical for journaling, metadata consistency, freeze/write accounting, quota reservations, and ENOSPC behavior. Risky areas include transaction roll reservation transfer, lazy superblock counter interactions, dirty cancel/shutdown behavior, precommit item ordering, and quota retry paths that drop locks or cancel transactions before retrying.
