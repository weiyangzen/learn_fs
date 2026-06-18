# File Research: sources/os/linux/linux/fs/btrfs/transaction.h

## Purpose

This header defines Btrfs transaction state, transaction/handle data structures, pending snapshot data, transaction type flags, abort helpers, and public transaction API declarations used by the rest of the filesystem.

## Core Types

`enum btrfs_trans_state`:
- Defines the transaction state machine from `TRANS_STATE_RUNNING` through `TRANS_STATE_COMPLETED`.

`struct btrfs_transaction`:
- Represents one filesystem-wide transaction.
- Tracks transaction id, writer counts, external writer counts, refcount, state, abort status, flags, dirty pages, pending snapshots, device updates, dirty block groups, dropped roots, delayed refs, pinned extents, deleted block groups, and pending ordered extents.
- Provides wait queues for writers, commit waiters, and pending ordered extents.
- Owns lists used during commit: `pending_snapshots`, `dev_update_list`, `switch_commits`, `dirty_bgs`, `io_bgs`, `dropped_roots`, and `deleted_bgs`.

`struct btrfs_trans_handle`:
- Per-task transaction handle.
- Tracks transid, reserved bytes, delayed-ref bytes, chunk metadata reservation, delayed-ref update counters, qgroup/csum deletion state, transaction pointer, block reservations, pending snapshot, type flags, abort status, fs info, new block groups, local delayed-ref reserve, and extent buffers with writeback inhibited by the handle.

`struct btrfs_pending_snapshot`:
- Carries all state needed to create a snapshot during commit.
- Includes dentry, parent dir inode, source root, new root item, resulting snapshot root, qgroup inheritance, path, block reserve, anon device, readonly flag, error, and list linkage.

## Transaction Type Flags

Internal bits include:
- `__TRANS_FREEZABLE`
- `__TRANS_START`
- `__TRANS_ATTACH`
- `__TRANS_JOIN`
- `__TRANS_JOIN_NOLOCK`
- `__TRANS_DUMMY`
- `__TRANS_JOIN_NOSTART`

Public combinations include:
- `TRANS_START`
- `TRANS_ATTACH`
- `TRANS_JOIN`
- `TRANS_JOIN_NOLOCK`
- `TRANS_JOIN_NOSTART`
- `TRANS_EXTWRITERS`

These flags determine whether a handle can start, attach, join, bypass some locking, or count as an external writer.

## Inline Helpers

- `btrfs_set_inode_last_trans()`: records the current transaction and log-subtransaction state on an inode.
- `btrfs_set_skip_qgroup()` / `btrfs_clear_skip_qgroup()`: set and clear a delayed-ref qgroup id to skip during accounting.
- `btrfs_abort_should_print_stack()`: suppresses stack traces for common external/resource errors like `-EIO`, `-EROFS`, and `-ENOMEM`.

## Abort Macro

`btrfs_abort_transaction(trans, error)`:
- Reports the first transaction abort since mount.
- Prints a stack trace only for errors likely to indicate a bug.
- Sets `BTRFS_FS_STATE_TRANS_ABORTED`.
- Delegates to `__btrfs_abort_transaction()` with function and line metadata.

## Public API Declarations

The header declares transaction start/join/attach/end/commit APIs, commit waiting, throttling, root recording, marked extent writeback, tree log extent waiting, transaction state checks, dropped root handling, chunk metadata release, abort implementation, and transaction cache init/exit.

## Important Invariants

- Transaction abort fields are accessed with `READ_ONCE()`/`WRITE_ONCE()` through `TRANS_ABORTED()` because abort status is not protected by a regular lock.
- `num_extwriters` must reach zero before commit can proceed past external-writer draining.
- `num_writers` must reach the commit holder before full commit work proceeds.
- `io_bgs` list consistency is guarded by transaction critical-section ordering rather than its own explicit lock.
- Pending ordered extents started by fast fsync must be waited before commit completes.

## Research Notes

This header is tightly coupled to `transaction.c`. The structs expose the concurrency and commit-ordering contract: writer accounting, state transitions, delayed refs, dirty block groups, snapshots, and abort propagation all meet here.
