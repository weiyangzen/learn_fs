# File Research: sources/local-fs/btrfs-linux/fs/btrfs/locking.h

## Purpose

Declares Btrfs tree-locking APIs, lockdep annotation helpers, lock nesting classes, and the DREW lock structure.

## Main Contents

- `BTRFS_WRITE_LOCK` and `BTRFS_READ_LOCK` path lock constants.
- `enum btrfs_lock_nesting` with subclasses for normal, COW, left/right siblings, split, and new-root locking.
- Lockdep wait-event annotation macros for transaction state, ordered extents, pending ordered extents, and io_uring inode-lock handoff.
- Tree lock/read lock prototypes and inline normal-nesting wrappers.
- Debug assertions for read/write-held extent buffer locks.
- DREW lock structure and operations.

## Key Invariants

- `BTRFS_NESTING_MAX <= MAX_LOCKDEP_SUBCLASSES` is statically asserted.
- io_uring encoded I/O explicitly models returning to userspace while inode locks are later released in task work.
