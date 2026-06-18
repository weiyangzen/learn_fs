# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_ihash.c

Read completely: 194 lines.

Implements the global in-core inode hash table keyed by device and inode number.

Core behavior:
- `ufs_ihashinit()` allocates the hash table sized from `initialvnodes` and seeds a SipHash key.
- `ufs_ihash()` hashes `(dev, ino)` using SipHash24.
- `ufs_ihashget()` searches for a matching inode, locks/references its vnode via `vget()`, retries on vnode recycle races, and rejects inodes being reclaimed or invalidated, including an ext2-specific nlink check.
- `ufs_ihashins()` locks the vnode, detects duplicate device/inode pairs, sets `IN_HASHED`, and inserts the inode.
- `ufs_ihashrem()` removes hashed inodes and clears diagnostics pointers.

Integration and risks:
- Comments flag missing/unfinished hash-list locking; correctness depends on broader vnode serialization assumptions.
- `ufs_ihashget()` contains an explicit workaround for grabbing a vnode while inactive/reclaim is in progress.
- Duplicate insert returns `EEXIST` after unlocking the new vnode.
