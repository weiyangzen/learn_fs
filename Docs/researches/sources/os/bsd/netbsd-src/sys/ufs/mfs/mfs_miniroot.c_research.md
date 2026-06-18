# File Research: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfs_miniroot.c

This file initializes an in-kernel MFS miniroot early in boot.

Key behavior:
- Defines `mfs_rootbase` and `mfs_rootsize`.
- `mfs_initminiroot(void *base)` validates a UFS1 superblock at `base + SBLOCK_UFS1`.
- Rejects invalid magic, invalid block size, or too-small superblock.
- Sets `rootfstype = MOUNT_MFS`, records root memory base/size, and sets synthetic `rootdev = makedev(255, 0)`.
- Panics if called more than once.

Role:
- Boot-time bridge from a memory image to an MFS root device mount.
