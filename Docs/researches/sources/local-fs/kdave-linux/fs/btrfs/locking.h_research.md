# File Research: sources/local-fs/kdave-linux/fs/btrfs/locking.h

## Purpose

`locking.h` declares Btrfs tree locking APIs, lockdep annotations, lock nesting classes, and the DREW lock structure/API.

## Key Definitions

The header defines `BTRFS_WRITE_LOCK` and `BTRFS_READ_LOCK` path lock markers, plus `enum btrfs_lock_nesting`. Nesting classes cover normal locks, COW blocks, left/right adjacent nodes, COW of adjacent nodes, split allocations, and new-root promotion. A `static_assert` enforces that the number of classes stays within `MAX_LOCKDEP_SUBCLASSES`.

It also defines transaction wait-state lockdep indices:

- `BTRFS_LOCKDEP_TRANS_COMMIT_PREP`
- `BTRFS_LOCKDEP_TRANS_UNBLOCKED`
- `BTRFS_LOCKDEP_TRANS_SUPER_COMMITTED`
- `BTRFS_LOCKDEP_TRANS_COMPLETED`

## Lockdep Annotation Macros

The header provides helper macros for wait-event lockdep modeling:

- `btrfs_might_wait_for_event()`
- `btrfs_lockdep_acquire()`
- `btrfs_lockdep_release()`
- `btrfs_lockdep_inode_acquire()`
- `btrfs_lockdep_inode_release()`
- transaction-state variants
- lockdep map initialization macros

The inode lockdep helpers are specifically used by io_uring encoded I/O, where Btrfs can return to userspace with an inode lock held until async completion.

## APIs

Tree lock functions include read/write nested locks, try read lock, root-node lock helpers, unlock helpers, and debug assertions. `btrfs_tree_unlock_rw()` dispatches based on stored path lock mode.

The DREW lock structure contains atomic `readers` and `writers` plus waitqueues for pending readers and writers. APIs include init, read lock/unlock, write lock/unlock, and try-write-lock.

## Integration Notes

This header is shared by tree manipulation, transaction wait code, ordered extent waits, io_uring lockdep annotations, and snapshot code. Its enum values and lockdep classes are part of Btrfs’s internal deadlock-prevention discipline.
