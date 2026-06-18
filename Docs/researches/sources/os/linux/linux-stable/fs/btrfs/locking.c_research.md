# File Research: sources/os/linux/linux-stable/fs/btrfs/locking.c

## Summary
Implements Btrfs tree extent-buffer locking, lockdep class assignment for btree nodes, root-node lock acquisition helpers, and the Btrfs DREW lock.

## Main Responsibilities
- Assigns lockdep classes for extent buffer locks by root objectid and tree level.
- Provides read/write lock wrappers around `extent_buffer->lock`.
- Safely locks current root nodes while handling root-node replacement races.
- Unlocks paths upward from a given btree level.
- Implements DREW, a double-reader-writer-exclusion lock where two classes exclude each other but not themselves.

## Key APIs
- `btrfs_set_buffer_lockdep_class()`.
- `btrfs_maybe_reset_lockdep_class()`.
- `btrfs_tree_read_lock_nested()`, `btrfs_tree_read_unlock()`, `btrfs_try_tree_read_lock()`.
- `btrfs_tree_lock_nested()`, `btrfs_tree_unlock()`.
- `btrfs_unlock_up_safe()`.
- `btrfs_lock_root_node()`, `btrfs_read_lock_root_node()`, `btrfs_try_read_lock_root_node()`.
- `btrfs_drew_lock_init()`, `btrfs_drew_write_lock()`, `btrfs_drew_try_write_lock()`, `btrfs_drew_write_unlock()`, `btrfs_drew_read_lock()`, `btrfs_drew_read_unlock()`.

## Important Behavior
Lockdep class keys are static and selected by special-purpose root objectid, with per-level names for `BTRFS_MAX_LEVEL == 8`. Unknown roots fall back to a default tree keyset.

Tree lock wrappers trace lock timing and unlock events. Under `CONFIG_BTRFS_DEBUG`, write locks record the owning pid in the extent buffer.

Root-node lock helpers loop: take a ref to the current root node, lock it, verify it is still `root->node`, and retry if the root changed concurrently.

DREW locks use atomic reader/writer counters plus wait queues. Readers have priority: writers yield if readers appear, and pending readers prevent new writers from entering.

## State and Synchronization
Tree locks are rw semaphores embedded in extent buffers. DREW uses atomic counters and memory barriers to order counter visibility against wait queue sleeping/wakeup.

## Risks
Lockdep class coverage is tied to `BTRFS_MAX_LEVEL` and the limited number of lockdep subclasses. DREW correctness depends on the atomic barriers around reader/writer count changes and wait conditions.
