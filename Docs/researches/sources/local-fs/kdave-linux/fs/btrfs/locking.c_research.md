# File Research: sources/local-fs/kdave-linux/fs/btrfs/locking.c

## Purpose

`locking.c` implements Btrfs tree-lock helpers for `extent_buffer` objects and the Btrfs DREW lock, a double-reader-writer-exclusion primitive used where two classes of users must exclude each other without excluding same-class users.

## Major Behavior

Under `CONFIG_DEBUG_LOCK_ALLOC`, the file defines lockdep class keysets for Btrfs tree block locks. Lock classes are selected by root objectid and tree level, with named classes for root, extent, chunk, device, checksum, quota, log, relocation, free-space, block-group, raid-stripe, remap, and default tree roots. `btrfs_set_buffer_lockdep_class()` assigns an extent buffer lock class by objectid and level, and `btrfs_maybe_reset_lockdep_class()` reapplies it when a root requests reset.

Extent-buffer locking wraps the underlying `rw_semaphore` in traceable helpers:

- `btrfs_tree_read_lock_nested()`
- `btrfs_try_tree_read_lock()`
- `btrfs_tree_read_unlock()`
- `btrfs_tree_lock_nested()`
- `btrfs_tree_unlock()`

Write locking records `lock_owner` under debug builds. Tracepoints measure lock acquisition and release.

Root node helpers loop until the locked extent buffer is still the current root node, because the root can change between grabbing and locking it:

- `btrfs_lock_root_node()`
- `btrfs_read_lock_root_node()`
- `btrfs_try_read_lock_root_node()`

`btrfs_unlock_up_safe()` unlocks a `btrfs_path` from a given level upward unless `keep_locks` is set.

The DREW lock uses atomic reader/writer counters and two waitqueues. Readers increment `readers` and wait until no writers remain. Writers fail or wait while readers exist, and readers are intentionally favored when pending.

## Dependencies and Integration

This file uses `extent_io.h`, `ctree.h`, trace events, lockdep, waitqueues, and atomic memory barriers. It underpins Btrfs tree traversal, COW, split/balance operations, snapshot coordination, and debug lock checking.

## Concurrency Notes

The code is lock-ordering infrastructure. Correctness depends on nesting subclasses, memory barriers after atomic counter changes, and root-node retry loops. The DREW implementation favors readers, which is intentional but can affect writer latency under sustained read pressure.
