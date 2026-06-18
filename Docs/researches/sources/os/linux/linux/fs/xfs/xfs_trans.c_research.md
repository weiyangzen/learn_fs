# File Research: sources/os/linux/linux/fs/xfs/xfs_trans.c

## Purpose

`xfs_trans.c` implements the core XFS transaction handle lifecycle: initialization of transaction reservations, allocation, reservation of log/space resources, superblock delta tracking, log item management, precommit processing, commit/cancel, transaction rolling, and helper allocators that combine transactions with inode locking and quota reservation.

It is the bridge between higher-level metadata mutations and the XFS log/CIL, quota, superblock counter, block reservation, and deferred-operation systems.

## Main Functions

- `xfs_trans_init()`: computes mount-specific transaction reservation values and emits reservation tracepoints when tracepoints are enabled.
- `xfs_trans_free()`: clears busy extents, emits free tracepoint, restores NOFS/writecount state, frees dquot accounting, and releases the transaction object.
- `xfs_trans_dup()`: creates the next transaction in a permanent-reservation chain, transferring remaining block/realtime reservations, sharing the log ticket, preserving selected flags, and moving deferred ops.
- `xfs_trans_reserve()`: reserves filesystem data blocks, log space, and realtime extents; unwinds earlier reservations on failure.
- `xfs_trans_alloc()` and `xfs_trans_alloc_empty()`: allocate transaction handles, apply freeze/writecount and NOFS context handling, reserve resources, and retry once after blockgc flush on ENOSPC.
- `xfs_trans_mod_sb()`: records superblock field deltas in the transaction and marks the transaction dirty and/or superblock-dirty as needed.
- `xfs_trans_apply_sb_deltas()`: joins the superblock buffer, applies logged on-disk deltas, and logs either contiguous counter fields or the whole superblock for noncontiguous changes.
- `xfs_trans_unreserve_and_mod_sb()`: releases unused reservations and applies transaction deltas to in-core counters and the in-core superblock.
- `xfs_trans_add_item()`, `xfs_trans_del_item()`, and `xfs_trans_free_items()`: manage transaction log item membership and release/abort cleanup.
- `xfs_trans_run_precommits()`: sorts log items to avoid lock-order inversions and runs dirty item precommit hooks.
- `__xfs_trans_commit()` and `xfs_trans_commit()`: apply superblock/quota deltas, finish deferred work for permanent transactions, run precommits, commit dirty transactions to the CIL, handle synchronous log forcing, or unreserve/free empty or failed transactions.
- `xfs_trans_cancel()`: aborts a transaction, cancels deferred ops, forces shutdown if dirty state cannot be safely rolled back, unreleases reservations, ungrants log tickets, aborts items, and frees the handle.
- `xfs_trans_roll()`: duplicates a permanent transaction, commits the current chunk with ticket regrant, restores NOFS context, and regrants log space for the next chunk.
- `xfs_trans_alloc_inode()`, `xfs_trans_reserve_more_inode()`, `xfs_trans_alloc_icreate()`, `xfs_trans_alloc_ichange()`, and `xfs_trans_alloc_dir()`: higher-level helpers that combine transaction allocation with inode locking, dquot attachment, quota reservation, retry after blockgc/quota cleanup, and directory update fallback behavior.

## Key Data Flow

1. A caller selects a precomputed `struct xfs_trans_res` and calls `xfs_trans_alloc()` or a helper such as `xfs_trans_alloc_inode()`.
2. `__xfs_trans_alloc()` allocates the transaction, takes write/freeze protection unless suppressed, saves the NOFS allocation context, initializes item/deferred/busy lists, and records the mount.
3. `xfs_trans_reserve()` deducts requested data blocks and realtime extents from global counters and obtains a log ticket through `xfs_log_reserve()`.
4. Metadata operations attach buffers, inodes, dquots, and deferred intents to the transaction. Superblock changes accumulate as deltas in `struct xfs_trans`.
5. Commit applies superblock and quota deltas, runs per-log-item precommit hooks, and either queues dirty items to the CIL via `xlog_cil_commit()` or unreserves resources for empty transactions.
6. Cancel releases reservations and log tickets; if dirty metadata cannot be backed out, it forces filesystem shutdown so dirty in-memory objects cannot later reach disk as valid metadata.
7. Permanent transactions can roll: remaining reservations and deferred operations move to a duplicate transaction while the old transaction commits and the shared ticket is regranted.

## Important Design Points

- Dirty transaction cancellation is treated as corruption risk. The code forces shutdown rather than attempting partial rollback of already-modified metadata.
- Lazy superblock counters affect whether changes are logged to the on-disk superblock. In-core counters still need updates even when on-disk counter logging is skipped.
- Realtime free-extent accounting has special handling: older non-rtgroup filesystems require `sb_frextents` to stay consistent on disk with the realtime bitmap, whereas rtgroups can treat it as a lazy counter.
- `XFS_TRANS_RES_FDBLKS` lets freed blocks replenish the transaction reservation before excess blocks return to the global pool, supporting chains of rolls that repeatedly free and allocate blocks.
- Precommit log items are sorted by `iop_sort` to reduce ABBA deadlocks when different transactions lock shared items such as inode cluster buffers.
- The transaction lifecycle is tightly coupled to `memalloc_nofs_save()` / `memalloc_nofs_restore()` so metadata operations do not recurse into filesystem reclaim unsafely.
- High-level inode/directory helpers retry quota or ENOSPC failures after blockgc cleanup, but only in bounded ways to avoid unbounded retry loops while locks may be involved.

## Cross-File Relationships

- Uses transaction types and exported prototypes from `xfs_trans.h`.
- Calls log manager APIs such as `xfs_log_reserve()`, `xfs_log_regrant()`, `xfs_log_ticket_regrant()`, `xfs_log_ticket_ungrant()`, `xfs_log_force_seq()`, and `xlog_cil_commit()`.
- Uses deferred operation APIs from `xfs_defer.h` to move, finish, and cancel deferred items.
- Uses quota APIs to attach dquots, reserve quota for block/inode/directory changes, apply deltas, and unreserve dquots.
- Uses superblock/mount helpers for lazy counters, realtime group behavior, realtime extent conversions, and in-core counter updates.
- Emits many tracepoints declared in `xfs_trace.h`, especially transaction, reservation, quota, and log item events.

## Risks / Review Notes

- Reservation unwind paths must keep global block, realtime extent, log ticket, and transaction counters synchronized; mistakes here cause leaks or false ENOSPC.
- Dirty-item precommit failures intentionally force shutdown. New `iop_precommit` implementations need strong guarantees because failure occurs after metadata has been modified.
- `xfs_trans_dup()` transfers remaining reservation capacity and marks the old transaction `XFS_TRANS_NO_WRITECOUNT`; changes to roll semantics must preserve writecount ownership.
- `xfs_trans_alloc_dir()` can downgrade to a reservationless directory update after ENOSPC/quota failure. Callers must honor the returned `dblocks` and `nospace_error`.
- Helpers that unlock or keep inode locks have precise contracts; changing cancel paths can easily introduce double unlocks or leaked locks.
