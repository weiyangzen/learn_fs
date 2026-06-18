# File Research: sources/os/linux/linux-stable/fs/afs/inode.c

## Summary
Owns AFS inode creation, status application, callback application, cache-cookie acquisition, getattr/setattr, drop, and eviction. It translates fileserver status records into Linux inode state and maintains coherency with AFS data-version and callback semantics.

## Main Responsibilities
- Initializes new inodes from AFS fetch status records.
- Applies status/callback updates to existing vnodes.
- Fetches status and root inode state from fileservers.
- Looks up/inserts inodes by AFS FID.
- Acquires fscache cookies for files, dirs, and symlinks.
- Implements `getattr`, `setattr`, inode drop, and eviction.
- Handles data-version jumps, deleted vnodes, and directory invalidation.

## Key APIs
- `afs_vnode_commit_status()`.
- `afs_fetch_status()`.
- `afs_iget()`.
- `afs_root_iget()`.
- `afs_getattr()`.
- `afs_setattr()`.
- `afs_drop_inode()`.
- `afs_evict_inode()`.

## Important Behavior
`afs_inode_init_from_status()` sets inode mode and operations based on AFS type. Symlinks with mode `0644` are treated as AFS mountpoints and exposed as automount directories.

`afs_apply_status()` rejects vnode type changes, updates owner/group/mode/timestamps/nlink, compares expected data-version deltas, invalidates directories or zaps file data on unexpected jumps, and updates netfs write sizes under inode locking.

`afs_vnode_commit_status()` handles inline error statuses such as `VNOVNODE`, speculative bulk-status results, callback promises, unlink nlink updates, and permit-cache updates.

`afs_setattr()` supports size, mode, uid, gid, mtime/touch-style changes. For truncation that only shortens local unwritten dirty data above remote size, it can avoid a server call and resize local state directly.

## State and Synchronization
Status and callback fields are protected by `vnode->cb_lock`. `validate_lock` blocks new writeback while setattr size changes are coordinated. Eviction waits for netfs I/O, flushes dirty directories/symlinks when needed, truncates pages, frees directory/symlink data, clears writeback state, relinquishes fscache, and drops permits/keys.

## Risks
Data-version handling is central: false expected-delta assumptions cause local invalidation, while missed jumps would leave stale data. `getattr()` reports server remote size for directories because local edited directory data may differ in allocation.
