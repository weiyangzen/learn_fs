# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_extern.h

This header declares the shared UFS operation surface.

Key contents:
- Declares vnode operations for access, create, lookup, directory mutation, readlink, remove, rename, strategy, whiteout, special device wrappers, and FIFO wrappers.
- Declares bmap helpers `ufs_bmaparray` and `ufs_getlbns`.
- Declares inode lifecycle and allocation/truncation helpers.
- Declares directory lookup/edit helpers.
- Declares rename helper routines used by LFS.
- Declares quota functions and quota command handling.
- Declares VFS-level UFS helpers.
- Declares vnode initialization, GOP allocation/update, and buffer I/O helpers.
- Exposes `ufs_direct_cache` and `ufs_hashlock`.

Role:
- The main internal contract between UFS, FFS, LFS-adjacent code, quota code, and vnode/VFS layers.
