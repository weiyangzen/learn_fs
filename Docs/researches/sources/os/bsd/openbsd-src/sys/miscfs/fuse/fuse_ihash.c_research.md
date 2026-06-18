# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_ihash.c

Purpose: Maintains the in-core FUSE inode hash table keyed by device and inode number.

Key behavior:
- `fuse_ihash()` hashes `(dev, ino)` with SipHash and a randomized key.
- `fuse_ihashinit()` allocates the hash table sized from `initialvnodes` and initializes the key.
- `fuse_ihashget()` looks up an existing node, obtains its vnode with `vget(LK_EXCLUSIVE)`, and retries if racing vnode lifecycle.
- `fuse_ihashins()` locks a new vnode, checks duplicate `(dev, ino)`, and inserts the node.
- `fuse_ihashrem()` removes a node from the hash chain and clears links under diagnostics.

Notable detail:
- Hash-list locking is marked with `XXXLOCKING` comments, making concurrency assumptions explicit but incomplete.
