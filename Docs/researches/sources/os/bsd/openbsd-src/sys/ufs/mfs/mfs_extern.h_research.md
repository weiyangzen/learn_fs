# File Research: sources/os/bsd/openbsd-src/sys/ufs/mfs/mfs_extern.h

Read completely: 64 lines.

Declares the public MFS interfaces used across the memory filesystem implementation.

Core definitions:
- Forward-declares kernel structures used by MFS VFS and vnode operations.
- Exposes `mfs_vops`.
- Declares VFS hooks: `mfs_mount()`, `mfs_start()`, `mfs_init()`, and `mfs_checkexp()`.
- Declares vnode/device hooks: `mfs_open()`, `mfs_ioctl()`, `mfs_strategy()`, `mfs_doio()`, `mfs_close()`, `mfs_inactive()`, `mfs_reclaim()`, and `mfs_print()`.

Integration and risks:
- MFS is implemented as an FFS filesystem backed by a synthetic block vnode, so these prototypes connect VFS mount setup to block-device strategy handling.
- `mfs_doio()` is the central data mover and must match `mfsnode` layout.
