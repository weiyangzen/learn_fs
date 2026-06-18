# File Research: sources/os/linux/linux/fs/Kconfig

Defines the top-level Linux filesystem Kconfig menu and sources filesystem subsystem Kconfig files.

Key behavior:
- Declares foundational filesystem config symbols such as `DCACHE_WORD_ACCESS`, `VALIDATE_FS_PARSER`, `FS_IOMAP`, `FS_STACK`, `BUFFER_HEAD`, and `LEGACY_DIRECT_IO`.
- Under `BLOCK`, includes major local/block filesystems such as ext2/ext4, JBD2, JFS, XFS, GFS2, OCFS2, Btrfs, NILFS2, F2FS, and zonefs.
- Defines DAX support options and POSIX ACL helper config.
- Includes filesystem crypto, verity, notify, quota, autofs, fuse, and overlayfs configuration.
- Defines the “Caches” submenu for netfs and cachefiles.
- Defines CD/DVD, DOS/FAT/EXFAT/NT, pseudo filesystems, tmpfs, hugetlbfs, configfs, and efivarfs menus.
- Defines `MISC_FILESYSTEMS` and sources ADFS, AFFS, and other miscellaneous filesystem Kconfigs.
- Defines `NETWORK_FILESYSTEMS` and sources NFS, NFSD, SunRPC, Ceph, SMB, Coda, AFS, and 9p Kconfigs.
- Includes NLS, DLM, Unicode, and `IO_WQ`.

Important interactions:
- `fs/adfs/Kconfig` and `fs/affs/Kconfig` are included under `MISC_FILESYSTEMS`.
- `fs/9p/Kconfig` is included under `NETWORK_FILESYSTEMS`.
