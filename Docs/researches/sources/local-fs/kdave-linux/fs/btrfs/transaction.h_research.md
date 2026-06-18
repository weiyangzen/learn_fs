# File Research: sources/local-fs/kdave-linux/fs/btrfs/transaction.h

## Purpose

This header defines the Btrfs transaction state machine types, transaction and transaction-handle structures, pending snapshot state, transaction type flags, abort helpers, qgroup skip helpers, and public transaction API prototypes.

## Key Definitions

- `BTRFS_TRANS_DIO_WRITE_STUB`: sentinel stored in `journal_info` for direct I/O write deadlock avoidance.
- `BTRFS_ROOT_TRANS_TAG`: radix-tree tag for roots participating in a transaction.
- `enum btrfs_trans_state`: transaction lifecycle states from `RUNNING` through `COMPLETED`.
- Transaction flags:
  - `BTRFS_TRANS_HAVE_FREE_BGS`
  - `BTRFS_TRANS_DIRTY_BG_RUN`
  - `BTRFS_TRANS_CACHE_ENOSPC`

## `struct btrfs_transaction`

Represents a filesystem-wide transaction. Important fields:
- `transid`: transaction generation.
- `num_extwriters`: external/user-visible writers that must drain before commit proceeds.
- `num_writers`: all transaction writers.
- `use_count`: lifetime refcount.
- `state`: transaction state, protected by `fs_info->trans_lock` for changes.
- `aborted`: abort errno.
- Wait queues for writers, commit waiters, and pending ordered extents.
- Lists for pending snapshots, device updates, dirty roots to switch, dirty/io block groups, dropped roots, deleted block groups.
- `dirty_pages` and `pinned_extents` extent I/O trees.
- `delayed_refs`: delayed reference root.
- Block group cache write coordination and dirty/dropped root locks.
- `pending_ordered`: fast-fsync ordered extents that commit must wait for.

## Transaction Type Flags

Internal bit flags:
- `__TRANS_FREEZABLE`
- `__TRANS_START`
- `__TRANS_ATTACH`
- `__TRANS_JOIN`
- `__TRANS_JOIN_NOLOCK`
- `__TRANS_DUMMY`
- `__TRANS_JOIN_NOSTART`

Public combinations:
- `TRANS_START`
- `TRANS_ATTACH`
- `TRANS_JOIN`
- `TRANS_JOIN_NOLOCK`
- `TRANS_JOIN_NOSTART`
- `TRANS_EXTWRITERS`

These flags drive transaction joining and commit blocking rules in `transaction.c`.

## `struct btrfs_trans_handle`

Represents a task’s handle into a transaction. Important fields:
- `transid`
- reservation counters: `bytes_reserved`, `delayed_refs_bytes_reserved`, `chunk_bytes_reserved`
- delayed-ref counters
- `transaction`
- active/original block reserves
- optional `pending_snapshot`
- `use_count`
- transaction type
- per-handle abort state
- mode booleans such as `adding_csums`, `allocating_chunk`, `removing_chunk`, `reloc_reserved`, `in_fsync`
- local `new_bgs` list
- local delayed-ref block reserve
- `writeback_inhibited_ebs` xarray for extent buffers whose writeback is inhibited by the handle

## `struct btrfs_pending_snapshot`

Carries all state needed for snapshot creation during commit:
- dentry, parent inode, source root, root item, resulting snapshot root.
- qgroup inheritance.
- path.
- operation block reserve.
- error status.
- preallocated anonymous block device number.
- readonly flag.
- transaction list node.

## Inline Helpers

- `btrfs_set_inode_last_trans()`: updates inode transaction/log tracking under inode lock.
- `btrfs_set_skip_qgroup()` / `btrfs_clear_skip_qgroup()`: set or clear delayed-ref qgroup id to skip during snapshot/qgroup accounting.
- `btrfs_abort_should_print_stack()`: suppresses stack traces for common external errors (`-EIO`, `-EROFS`, `-ENOMEM`) and prints for likely bug-triggered errors.

## Abort Macro

`btrfs_abort_transaction(trans, error)`:
- Reports the first transaction abort since mount.
- Optionally emits a warning/stack trace depending on error class.
- Calls `__btrfs_abort_transaction()` with function, line, error, and first-hit state.

## Public API Surface

The header exports start/join/attach/end/commit/wait APIs, transaction throttling, root recording, dirty extent write/wait helpers, dropped/dead root helpers, chunk metadata release, abort implementation, and module init/exit for the transaction handle cache.

## Research Notes

This header establishes the transaction contract used throughout Btrfs. The most important design signal is the distinction between a global `btrfs_transaction` and per-task `btrfs_trans_handle`, plus the explicit separation of external writers from all writers for commit ordering.
