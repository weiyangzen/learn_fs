# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_defer.h

## Role
`xfs_defer.h` declares the public deferred-operation framework used by XFS metadata update code and log recovery.

## Main Definitions
- `struct xfs_defer_pending` represents one pending batch of work for a single operation type, including work list, intent item, done item, hook table, count, and flags.
- `XFS_DEFER_PAUSED` marks a deferred item whose intent exists but whose work should not be finished yet.
- `struct xfs_defer_op_type` is the operation-specific vtable for intent creation, abort, done creation, item finishing, cleanup, cancellation, recovery, and intent relogging.
- `struct xfs_defer_resources` stores buffers and inodes that must be held across a transaction roll.
- `struct xfs_defer_capture` stores a detached deferred-operation chain and transaction state so recovery can continue it later.

## Exported API
- Queueing and finishing: `xfs_defer_add`, `xfs_defer_finish_noroll`, `xfs_defer_finish`, `xfs_defer_finish_one`, `xfs_defer_cancel`, and `xfs_defer_move`.
- Pausing: `xfs_defer_item_pause`, `xfs_defer_item_unpause`, and `xfs_defer_add_barrier`.
- Recovery: `xfs_defer_start_recovery`, `xfs_defer_cancel_recovery`, `xfs_defer_finish_recovery`, `xfs_defer_ops_capture_and_commit`, `xfs_defer_ops_continue`, and `xfs_defer_resources_rele`.
- Cache lifecycle: `xfs_defer_init_item_caches` and `xfs_defer_destroy_item_caches`.

## Registered Operation Types
The header exposes defer types for bmap updates, refcount updates, realtime refcount updates, rmap updates, realtime rmap updates, extent frees, AGFL frees, realtime extent frees, attrs, and exchange-map operations.

## Design Notes
- The framework is intentionally generic: actual filesystem operation logic lives in each `xfs_defer_op_type`, while the common code handles transaction ordering and recovery.
- The capture structure is explicitly recovery-oriented and saves enough reservation and held-resource state to reconnect deferred work to a new transaction.

## Research Notes
This header is the compact contract between metadata subsystems and the deferred-ops engine. New deferred work types plug in by defining an `xfs_defer_op_type` and using `xfs_defer_add`.
