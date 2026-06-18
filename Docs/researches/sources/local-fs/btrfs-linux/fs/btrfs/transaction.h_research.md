# File Research: sources/local-fs/btrfs-linux/fs/btrfs/transaction.h

## Summary
Declares Btrfs transaction state, transaction and transaction-handle structures, pending snapshot state, transaction type flags, abort helpers, qgroup skip helpers, and public transaction APIs.

## Main Responsibilities
- Define `enum btrfs_trans_state` commit lifecycle states.
- Define `struct btrfs_transaction` for global transaction state.
- Define `struct btrfs_trans_handle` for per-task participation and reservations.
- Define `struct btrfs_pending_snapshot` for snapshot work deferred into commit.
- Provide inline helpers for inode last-trans updates and qgroup skip-id state.
- Provide the `btrfs_abort_transaction()` macro and abort stack-print policy.
- Export transaction start/join/commit/wait/root/dead-root APIs.

## Key Structures
`struct btrfs_transaction` stores transid, external/total writer counts, refcount, state, abort code, dirty pages, wait queues, pending snapshots, device updates, roots to switch, dirty/io/deleted block groups, dropped roots, pinned extents, delayed refs, and pending ordered extents.

`struct btrfs_trans_handle` stores reservation accounting, chunk metadata reservation, delayed-ref counters, transaction pointer, block reservation pointers, pending snapshot pointer, type flags, abort code, qgroup/csum/chunk flags, fsync flag, new block groups, local delayed-ref reserve, and inhibited extent-buffer writeback xarray.

`struct btrfs_pending_snapshot` captures dentry, parent dir inode, source root, copied root item, resulting root, qgroup inheritance, path, block reserve, error, anon device number, readonly flag, and list linkage.

## Important Behavior
Transaction type bits distinguish start, attach, join, join-nolock, dummy, and join-nostart modes. `TRANS_EXTWRITERS` covers transaction starts and attaches, which must drain before the commit critical section proceeds.

`TRANS_ABORTED()` uses `READ_ONCE()` because abort state is lockless and can change between checks, though once nonzero it does not change.

`btrfs_abort_transaction()` reports only the first abort since mount with optional stack trace. It suppresses stack traces for common external failures like `-EIO`, `-EROFS`, and `-ENOMEM`.

## Risks
The header encodes concurrency contracts relied on by many files. Changing state ordering, transaction type bits, or abort semantics affects commit blocking, freeze behavior, fsync interaction, qgroup accounting, and cleanup paths across the filesystem.
