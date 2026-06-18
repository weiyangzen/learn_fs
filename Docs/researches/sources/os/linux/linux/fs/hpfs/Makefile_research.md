# File Research: sources/os/linux/linux/fs/hpfs/Makefile

Purpose: Builds the HPFS filesystem module/object.

Key content:
- Adds `hpfs.o` under `obj-$(CONFIG_HPFS_FS)`.
- Links HPFS from allocation, anode, buffer, dentry, directory, dnode, EA, file, inode, map, name, namei, and super objects.

Dependencies and integration:
- `super.o` is part of the final object but outside this work item.

Risk notes:
- Object list shows HPFS is tightly coupled; most modules share structures and prototypes through `hpfs_fn.h`.
