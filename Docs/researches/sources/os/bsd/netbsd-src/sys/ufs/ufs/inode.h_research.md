# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/inode.h

This header defines the in-core UFS inode and supporting metadata.

Key contents:
- Defines `struct ufs_lookup_results`, used to carry lookup side effects into directory mutation operations.
- Defines per-filesystem inode extensions for FFS, ext2fs, and LFS.
- Defines `struct inode`, including genfs node, vnode, mount, device vnode, inode number, filesystem union, quotas, modrev, locks, directory lookup scratch state, dirhash, extended attribute transaction fields, cached inode metadata, and on-disk dinode pointers.
- Provides many field aliases for UFS1 and UFS2 dinode access.
- Defines inode state flags such as `IN_ACCESS`, `IN_CHANGE`, `IN_UPDATE`, `IN_MODIFIED`, and `IN_SPACECOUNTED`.
- Provides `DIP`, `DIP_ASSIGN`, `DIP_ADD`, `SHORTLINK`, `VTOI`, and `ITOV`.
- Defines `struct indir` for indirect block traversal and `struct ufid` for file handles.

Role:
- Central in-memory representation shared by UFS, FFS, LFS-derived ULFS, and ext2fs-adjacent code.
