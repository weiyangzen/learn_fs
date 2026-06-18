# File Research: sources/os/linux/linux/fs/gfs2/Makefile

Builds the GFS2 kernel module/object from its component source files.

Key behavior:
- Adds `-I$(src)` to compilation flags.
- Builds `gfs2.o` when `CONFIG_GFS2_FS` is enabled.
- Core objects include ACL, bmap, dir, xattr, glock/glops, log/lops, metadata I/O, inode, quota, recovery, resource groups, superblock, transactions, util, file, export, dentry, and mount logic.
- Adds `lock_dlm.o` when `CONFIG_GFS2_FS_LOCKING_DLM` is enabled.

Integration:
- Mirrors the Kconfig split between core filesystem and DLM cluster locking.
