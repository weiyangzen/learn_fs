# File Research: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_fifoops.c

Tmpfs vnode operation vector specialization for named pipes.

Key responsibilities:
- Implements `tmpfs_fifo_close()` to mark the tmpfs node accessed, update timestamps, then delegate close behavior to `fifo_specops.vop_close`.
- Defines `tmpfs_fifoop_entries`, using `fifo_specops` as the default operation vector while overriding close, reclaim, access, getattr, setattr, pathconf, print, add-writecount, and fast-path lookup handlers.
- Registers the FIFO vnode operation vector with `VFS_VOP_VECTOR_REGISTER`.

Dependencies:
- Tmpfs node conversion and timestamp helpers from `tmpfs.h`.
- Tmpfs generic vnode operations from `tmpfs_vnops.h`.
- FreeBSD FIFO special vnode operations `fifo_specops`.

Notable risks:
- FIFO operations are mostly delegated, so tmpfs-specific metadata updates must happen in the few overridden hooks.
- Fast-path lookup execute/symlink operations return `VOP_EAGAIN`, forcing fallback to locked lookup paths.
