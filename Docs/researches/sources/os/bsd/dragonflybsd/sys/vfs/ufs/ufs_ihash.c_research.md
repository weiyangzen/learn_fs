# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_ihash.c

## Purpose

Maintains the per-mount in-core inode hash table keyed by inode number and device. This lets UFS find existing vnodes/inodes and prevents duplicate incore inodes for the same on-disk inode.

## Main Functions

- `ufs_ihashinit(struct ufsmount *ump)`: allocates the hash table sized by `vfs_inodehashsize()` and stores a mask in `um_ihash`.
- `ufs_ihashuninit(struct ufsmount *ump)`: frees the hash table.
- `ufs_ihashlookup(struct ufsmount *ump, cdev_t dev, ino_t inum)`: returns an incore vnode without locking or waiting.
- `ufs_ihashget(struct ufsmount *ump, cdev_t dev, ino_t inum)`: finds and locks the vnode, retrying if the vnode changes while blocked.
- `ufs_ihashcheck(struct ufsmount *ump, cdev_t dev, ino_t inum)`: returns whether an inode is present. Used to interlock inode free/reuse.
- `ufs_ihashins(struct ufsmount *ump, struct inode *ip)`: inserts an inode unless a duplicate exists, marking `IN_HASHED`.
- `ufs_ihashrem(struct ufsmount *ump, struct inode *ip)`: removes a hashed inode and clears `IN_HASHED`.

## Important Behavior

The hash bucket is `inum & ump->um_ihash`, where `um_ihash` is one less than the allocated hash size. Insert walks to the bucket tail and returns `EBUSY` if the same device/inode pair already exists.

`ufs_ihashget()` uses `vget()` and then rechecks the hash chain after potential blocking to ensure the vnode still represents the requested inode.

## Dependencies And Integration Points

Uses `struct ufsmount` fields `um_ihashtbl` and `um_ihash`. Called during inode allocation/loading and reclaim paths. `ufs_reclaim()` removes inodes from this hash.

## Notes For Future Work

- The implementation assumes external synchronization sufficient for bucket list mutation in this kernel context.
- `ufs_ihashlookup()` intentionally returns even if the vnode is locked; callers needing a locked vnode must use `ufs_ihashget()`.
