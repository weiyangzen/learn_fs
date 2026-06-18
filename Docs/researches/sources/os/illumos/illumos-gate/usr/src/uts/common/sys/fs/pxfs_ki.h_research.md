# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pxfs_ki.h

This header defines kernel interface stubs for PXFS asynchronous I/O.

Interfaces:
- `clpxfs_aio_write(vnode_t *, struct aio_req *, cred_t *)`.
- `clpxfs_aio_read(vnode_t *, struct aio_req *, cred_t *)`.

Dependencies and relationships:
- Includes VFS, vnode, and AIO request definitions.
- The comments identify these as kernel interface stubs to PXFS routines, specifically for KAIO integration.
- Related to PXFS lock hooks in `flock_impl.h`.
