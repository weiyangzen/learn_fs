# File Research: sources/os/linux/linux/fs/btrfs/locking.h

This header defines Btrfs lock nesting classes, lockdep helper macros, tree-lock APIs, and the DREW lock type.

Key definitions:
- `BTRFS_WRITE_LOCK` and `BTRFS_READ_LOCK` encode path lock state.
- `enum btrfs_lock_nesting` defines lockdep subclasses for normal, COW, left/right sibling, left/right COW, split, and new-root locking.
- `enum btrfs_lockdep_trans_states` defines transaction state wait-event lockdep maps.
- `struct btrfs_drew_lock` stores reader/writer counters and waitqueues.

Exported APIs:
- Tree lock wrappers: `btrfs_tree_lock_nested()`, `btrfs_tree_lock()`, `btrfs_tree_unlock()`, `btrfs_tree_read_lock_nested()`, `btrfs_tree_read_lock()`, `btrfs_tree_read_unlock()`, and `btrfs_try_tree_read_lock()`.
- Root-node locking: `btrfs_lock_root_node()`, `btrfs_read_lock_root_node()`, and `btrfs_try_read_lock_root_node()`.
- Path unlocking: `btrfs_unlock_up_safe()` and `btrfs_tree_unlock_rw()`.
- DREW lock lifecycle and operations.
- Lockdep class hooks for extent buffers when debug lock allocation is enabled.

Lockdep helpers:
- `btrfs_might_wait_for_event()`, `btrfs_lockdep_acquire()`, and `btrfs_lockdep_release()` annotate wait-event conditions.
- `btrfs_lockdep_inode_acquire()` and `btrfs_lockdep_inode_release()` model io_uring encoded I/O returning with an inode lock held.
- Transaction state helpers annotate transaction wait-state transitions.
- Static assertion prevents adding more nesting classes than lockdep supports.

Design notes:
- This header centralizes lock ordering documentation for Btrfs btree operations.
- The explicit nesting classes are important because tree balancing and COW frequently lock peer or replacement nodes while a related node is already locked.
