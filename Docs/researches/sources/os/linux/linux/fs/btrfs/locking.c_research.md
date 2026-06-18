# File Research: sources/os/linux/linux/fs/btrfs/locking.c

This file implements extent-buffer tree locking wrappers, Btrfs lockdep class assignment, and the DREW double-reader/writer-exclusion lock used by snapshot coordination.

Core responsibilities:
- Assign lockdep classes to extent-buffer locks based on root objectid and tree level.
- Provide read/write lock wrappers around `extent_buffer->lock`, with tracing and lockdep nesting.
- Lock the current root node safely even if the root pointer changes while taking references.
- Unlock Btrfs path nodes above a given level.
- Implement `btrfs_drew_lock`, a lock that excludes readers from writers but allows reader-reader and writer-writer sharing.

Key mechanisms:
- Under `CONFIG_DEBUG_LOCK_ALLOC`, static keysets are defined for special roots such as root, extent, chunk, dev, csum, quota, log, reloc, uuid, free-space, block-group, raid-stripe, remap, and generic tree roots.
- `btrfs_set_buffer_lockdep_class()` maps an extent buffer to a root/level lock class.
- `btrfs_maybe_reset_lockdep_class()` reapplies classes for roots marked with `BTRFS_ROOT_RESET_LOCKDEP_CLASS`.
- `btrfs_tree_read_lock_nested()`, `btrfs_try_tree_read_lock()`, `btrfs_tree_read_unlock()`, `btrfs_tree_lock_nested()`, and `btrfs_tree_unlock()` wrap rwsem operations with tracepoints.
- `btrfs_lock_root_node()`, `btrfs_read_lock_root_node()`, and `btrfs_try_read_lock_root_node()` loop until the locked buffer still matches `root->node`.
- `btrfs_unlock_up_safe()` releases held path locks from a level upward unless `path->keep_locks` is set.
- DREW lock read/write paths use atomic counters, waitqueues, and memory barriers to ensure pending readers prevent new writers and waiters observe counter transitions.

Important invariants:
- Lockdep setup assumes `BTRFS_MAX_LEVEL == 8`.
- Tree locks preserve standard rwsem semantics: writer excludes all, readers share.
- DREW locks prefer readers when readers and writers race.
- Root-node locking must validate the locked buffer against the current root node before returning it.

Cross-file relationships:
- Declarations and inline helpers live in `locking.h`.
- Used throughout btree search/update, snapshot creation, relocation, encoded I/O lockdep handoff, and transaction wait annotations.
