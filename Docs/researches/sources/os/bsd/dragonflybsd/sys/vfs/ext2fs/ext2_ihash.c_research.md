# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_ihash.c

This file implements the in-core ext2 inode hash table keyed by device and inode number. It is adapted from UFS inode hashing and uses a DragonFly LWKT token for serialization.

Key responsibilities:
- Allocate and free the global inode hash table.
- Look up active inodes and safely acquire their vnodes.
- Insert newly loaded/allocated inodes.
- Remove reclaimed inodes from the hash.

Important functions:
- `ext2_ihashinit`: Allocates a zeroed hash table sized by `vfs_inodehashsize` and initializes `ext2_ihash_token`.
- `ext2_ihashuninit`: Frees the hash table under the token.
- `ext2_ihashget`: Searches by `cdev_t` and inode number, uses `vget` to lock the vnode, and revalidates after blocking.
- `ext2_ihashins`: Inserts an inode if no matching `(dev, ino)` exists; sets `IN_HASHED`.
- `ext2_ihashrem`: Removes a hashed inode and clears `IN_HASHED`.

Important interactions:
- Used by vnode allocation/loading and reclaim paths (`ext2_valloc`, `ext2_reclaim`, and mount/vnode code outside this group).

Notable behavior:
- The hash macro uses `minor(device) + inum`.
- `ext2_ihashget` loops to handle races where an inode is reclaimed or replaced while `vget` blocks.
