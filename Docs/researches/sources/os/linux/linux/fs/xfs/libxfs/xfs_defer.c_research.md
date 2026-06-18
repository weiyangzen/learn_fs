# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_defer.c

## Scope

This file implements XFS deferred operations: batching metadata work, logging intent/done items for crash recovery, rolling transactions while preserving held resources, finishing or canceling pending work, pausing work items, capturing deferred chains during log recovery, and initializing intent-item caches.

## Main Interfaces

- Work queueing and lifecycle: `xfs_defer_add()`, `xfs_defer_add_barrier()`, `xfs_defer_cancel()`, `xfs_defer_move()`.
- Finish paths: `xfs_defer_finish_noroll()`, `xfs_defer_finish()`, `xfs_defer_finish_one()`.
- Pause controls: `xfs_defer_item_pause()`, `xfs_defer_item_unpause()`.
- Recovery setup: `xfs_defer_start_recovery()`, `xfs_defer_cancel_recovery()`, `xfs_defer_finish_recovery()`.
- Recovery capture/continue: `xfs_defer_ops_capture_and_commit()`, `xfs_defer_ops_continue()`, `xfs_defer_ops_capture_abort()`, `xfs_defer_resources_rele()`.
- Cache lifecycle: `xfs_defer_init_item_caches()`, `xfs_defer_destroy_item_caches()`.

## Control Flow And Behavior

Deferred work is grouped into `xfs_defer_pending` records by operation type. New work is appended to the last compatible pending item unless that item has already logged an intent, is paused, or has reached the operation’s `max_items` limit.

Finishing deferred work first creates log intent items for all intake work, isolates paused items, moves active work to a pending list, rolls the transaction if needed, and finishes the first pending item. Finishing a pending item creates a done item, calls the operation type’s `finish_item` for each work record, and frees the pending record when complete.

If `finish_item` returns `-EAGAIN`, the item is restored to the work list and a replacement intent is logged so the caller can roll to a fresh transaction and resume safely. The code also relogs old intent items when log-tail pressure requires moving the log forward.

Transaction rolls preserve held buffers and inodes. Buffers with `XFS_BLI_HOLD` are rejoined and optionally re-marked ordered; inodes joined without unlock flags are relogged and rejoined to the new transaction.

Recovery can capture a chain of deferred ops into `xfs_defer_capture`, commit the current transaction with fresh intents logged, and later continue the captured work in a new transaction after relocking saved inodes and buffers.

## State And Data Structures

- `xfs_defer_pending_cache` allocates pending work records.
- `xfs_defer_pending` tracks work list, intent item, done item, op type, count, and flags.
- `xfs_defer_resources` records held buffers, ordered buffer bitmap, and inodes that must survive transaction rolls.
- `xfs_defer_capture` stores a captured dfops list, transaction flags, block/log reservations, and held resources.
- `xfs_defer_op_type` callbacks define operation-specific intent creation, done creation, item finish, cleanup, cancellation, recovery, and relogging.

## Dependencies

Integrates with transaction internals, log items, AIL/log-tail push state, buffer and inode log items, rmap/refcount/bmap/extfree/attr/exchange intent caches, metadata health shutdown, and tracepoints.

## Risks And Invariants

- Deferred operations require permanent log reservations; most entry points assert `XFS_TRANS_PERM_LOG_RES`.
- Intent and done items must be logged in the correct transaction order to preserve crash replay guarantees.
- `-EAGAIN` handling depends on the finish callback updating the current work item to represent unfinished work.
- Held resource capture is bounded by `XFS_DEFER_OPS_NR_INODES` and `XFS_DEFER_OPS_NR_BUFS`; exceeding those bounds indicates corruption or incorrect caller behavior.
- Error paths abort outstanding intents, force shutdown for in-core corruption, and cancel pending work to avoid replay ambiguity.
