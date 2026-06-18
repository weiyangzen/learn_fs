# File Research: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfs_extern.h

This header declares the external MFS VFS and vnode operation interface.

Key contents:
- Declares `VFS_PROTOS(mfs)`.
- Declares `mfs_initminiroot`.
- Declares vnode operations such as `mfs_open`, `mfs_strategy`, `mfs_bmap`, `mfs_close`, `mfs_inactive`, `mfs_reclaim`, `mfs_print`, and `mfs_fsync`.
- Declares `mfs_doio`, the core buffer-to-memory transfer helper.
- Under `_KERNEL`, exposes global `mfs_lock`, `mfs_rootbase`, and `mfs_rootsize`.

Role:
- Public kernel header connecting MFS mount code, vnode operation code, and miniroot setup.
