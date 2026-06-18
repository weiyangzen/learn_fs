# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_defer.c

## Role
`xfs_defer.c` implements XFS deferred operations: a generic framework for work that must be split across rolling transactions while preserving crash recovery through log intent and log done items.

## Main Responsibilities
- Queue typed deferred work items on a transaction.
- Create log intent items before rolling transactions.
- Create log done items as work is completed.
- Finish deferred work one item type at a time while allowing continuations through `-EAGAIN`.
- Relog old intent items to avoid pinning the log tail.
- Save and restore held buffers/inodes across transaction rolls.
- Capture deferred operation chains during log recovery and continue them later.
- Initialize and destroy caches for deferred operation pending items and all registered intent item types.

## Deferred Operation Model
- `struct xfs_defer_pending` tracks one pending operation type, a work list, an optional intent item, an optional done item, item count, flags, and its `xfs_defer_op_type`.
- `struct xfs_defer_op_type` supplies operation-specific hooks for creating/aborting intents, creating done items, finishing work, cleanup, canceling work, recovering work, and relogging intents.
- Work first enters `tp->t_dfops`, then intent creation and transaction rolls move it into pending processing.
- Barrier deferred ops are represented by `xfs_barrier_defer_type` and force separation between otherwise adjacent deferred work batches.

## Important Functions
- `xfs_defer_add` appends a work item to the last compatible pending item, or allocates a new pending item if type, logged state, pause state, or max-items limits prevent append.
- `xfs_defer_create_intent` and `xfs_defer_create_intents` create log intents for deferred work and attach them to the transaction.
- `xfs_defer_create_done` creates intent-done log items and marks the transaction dirty.
- `xfs_defer_finish_one` creates the done item, calls the type-specific `finish_item` hook for each work item, and handles `-EAGAIN` by rebuilding a new intent for unfinished work.
- `xfs_defer_finish_noroll` is the core finishing loop: create intents, isolate paused items, splice intake to pending, roll transactions when needed, relog old intents, finish the first pending item, and abort/shutdown on unrecoverable errors.
- `xfs_defer_finish` wraps the no-roll path and rolls once more if the outgoing transaction is dirty.
- `xfs_defer_cancel` aborts outstanding intents and cancels all queued work.
- `xfs_defer_trans_roll`, `xfs_defer_save_resources`, and `xfs_defer_restore_resources` preserve selected buffers and inodes across transaction rolls.
- `xfs_defer_ops_capture_and_commit`, `xfs_defer_ops_continue`, and `xfs_defer_resources_rele` implement recovery-time capture and continuation.

## Error Handling and Recovery
- If finishing fails with an error other than `-EAGAIN`, the code aborts pending intents, forces a corrupt in-core shutdown, cancels pending and transaction dfops, and returns the error.
- `-EAGAIN` from an operation-specific finisher is a controlled continuation request. The unfinished item is requeued and a new intent is logged in the same transaction context.
- Recovery starts with `xfs_defer_start_recovery`, cancels through `xfs_defer_cancel_recovery`, and finishes through the operation type's `recover_work`.
- Captured recovery chains store deferred ops, low-space flags, block reservations, realtime reservations, log reservation, and held resources.

## Invariants
- Deferred finishing requires permanent log reservation (`XFS_TRANS_PERM_LOG_RES`).
- Paused items are isolated and requeued without being finished until unpaused.
- Held buffer and inode counts are bounded by `XFS_DEFER_OPS_NR_BUFS` and `XFS_DEFER_OPS_NR_INODES`.
- Intent relogging is allowed to be racy because a false negative only slows log-tail movement.

## Dependencies
This file coordinates with transaction internals, log items, buffer and inode log items, rmap/refcount/bmap/extent-free/attr/exchange-map intent caches, allocation and btree subsystems, and log recovery.

## Research Notes
This file is the crash-safety and transaction-splitting backbone for complex XFS metadata updates. Its main abstraction is operation-specific intent/done handling under a generic queueing and transaction roll engine.
