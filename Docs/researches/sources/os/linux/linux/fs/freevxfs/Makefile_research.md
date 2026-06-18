# File Research: sources/os/linux/linux/fs/freevxfs/Makefile

Read status: complete, 9 lines.

Purpose: builds the FreeVxFS module.

Content:
- `obj-$(CONFIG_VXFS_FS) += freevxfs.o`.
- Links `freevxfs.o` from `vxfs_bmap.o`, `vxfs_fshead.o`, `vxfs_immed.o`, `vxfs_inode.o`, `vxfs_lookup.o`, `vxfs_olt.o`, `vxfs_subr.o`, and `vxfs_super.o`.

Integration note: all implementation files in this batch are compiled into one module when `CONFIG_VXFS_FS` is enabled.
