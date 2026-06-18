# File Research: sources/os/linux/linux-stable/fs/btrfs/transaction.h

## Role

Public transaction interface and core transaction data structures for Btrfs.

## Key Types

- `enum btrfs_trans_state`: transaction lifecycle states from running through completed.
- `struct btrfs_transaction`: filesystem-wide transaction object containing transid, writer counters, state/abort status, dirty page tree, pending snapshots, device updates, dirty/io/deleted block groups, dropped roots, delayed refs, pinned extents, and wait queues.
- `struct btrfs_trans_handle`: per-task handle containing reservations, delayed-ref accounting, current block reserve, pending snapshot pointer, handle type, abort status, qgroup/checksum/chunk flags, fsync marker, new block groups, delayed-ref reserve, and inhibited writeback xarray.
- `struct btrfs_pending_snapshot`: queued snapshot creation request with dentry, parent inode, source root, new root item, qgroup inheritance, path, block reserve, anon dev, readonly flag, and result error.

## Transaction Modes

Internal bits distinguish freezable starts, attach, join, join-nolock, dummy, and join-nostart. Public mode macros include:

- `TRANS_START`
- `TRANS_ATTACH`
- `TRANS_JOIN`
- `TRANS_JOIN_NOLOCK`
- `TRANS_JOIN_NOSTART`
- `TRANS_EXTWRITERS`

## Inline Helpers

- `btrfs_set_inode_last_trans()`: updates inode transaction/log tracking.
- `btrfs_set_skip_qgroup()` / `btrfs_clear_skip_qgroup()`: set delayed-ref qgroup skip id for snapshot accounting.
- `btrfs_abort_should_print_stack()`: suppresses stack traces for common external/error conditions.
- `btrfs_abort_transaction()`: macro that records first abort, logs/warns, and calls `__btrfs_abort_transaction()` with callsite.

## Exported API

Declares transaction start/join/attach/end/commit functions, async/current commit helpers, commit wait, throttling, root recording, dirty extent write/wait helpers, transaction blocked checks, dropped/dead root handling, chunk metadata release, abort implementation, and slab-cache init/exit.
