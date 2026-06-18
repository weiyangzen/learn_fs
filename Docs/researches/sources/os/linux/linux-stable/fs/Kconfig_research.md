# File Research: sources/os/linux/linux-stable/fs/Kconfig
- Purpose: Top-level Linux filesystem Kconfig menu.
- Main role: Defines global filesystem infrastructure options and sources per-filesystem Kconfig files.
- Infrastructure options: Includes dcache word access, fs parser validation, iomap, stacking, buffer heads, direct I/O, DAX, POSIX ACLs, exportfs, file locking, crypto, verity, notify, quota, caches, pseudo filesystems, and network filesystems.
- Local filesystem integration: Sources ext, jfs, xfs, gfs2, ocfs2, btrfs, nilfs2, f2fs, zonefs, ADFS, AFFS, and many other filesystem menus.
- Network integration: Sources NFS/NFSD, SUNRPC, Ceph, SMB, Coda, AFS, and 9P.
- Research notes: This file determines menu hierarchy and shared config symbols that lower-level filesystem code depends on.
