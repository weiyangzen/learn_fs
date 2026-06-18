# File Research: sources/os/linux/linux-stable/fs/btrfs/locking.h

## Summary
Defines Btrfs btree lock nesting constants, lockdep annotation helpers, tree-lock APIs, assertion helpers, and the DREW lock structure/API.

## Main Contents
- `BTRFS_WRITE_LOCK` and `BTRFS_READ_LOCK`.
- `enum btrfs_lock_nesting` subclasses for normal, COW, left/right sibling, split, and new-root locking.
- `enum btrfs_lockdep_trans_states`.
- Lockdep macros for wait events, transaction state waits, and io_uring encoded I/O inode lock release/reacquire modeling.
- Tree lock function declarations and root-node lock helpers.
- Debug-only tree lock assertion helpers.
- `struct btrfs_drew_lock` and DREW lock declarations.
- Debug lockdep class reset declarations.

## Important Details
The nesting enum intentionally consumes the available `MAX_LOCKDEP_SUBCLASSES` budget and has a `static_assert()` to prevent silent overflow.

`btrfs_tree_unlock_rw()` dispatches unlock by stored path lock mode and `BUG()`s on invalid mode.

The io_uring lockdep macros model the fact that Btrfs encoded io_uring reads can return to userspace while the inode rwsem remains held and is later released in task work.

## Risks
Adding new btree lock nesting modes requires revisiting lockdep subclass limits. Callers storing lock modes in paths must keep values restricted to `BTRFS_WRITE_LOCK` or `BTRFS_READ_LOCK`.
