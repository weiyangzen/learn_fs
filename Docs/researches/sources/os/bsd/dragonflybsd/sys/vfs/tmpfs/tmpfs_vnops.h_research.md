# File Research: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_vnops.h

Kernel-only tmpfs vnode operations declaration header.

Key responsibilities:
- Enforces kernel-only inclusion with a preprocessor error for non-`_KERNEL` builds.
- Exports tmpfs VOP operation tables for ordinary vnodes and FIFO vnodes: `tmpfs_vnode_vops` and `tmpfs_fifo_vops`.
- Exports the read-mostly `tmpfs_bufcache_mode` tuning variable.
- Declares core tmpfs vnode operation entry points implemented in `tmpfs_vnops.c`: access checks, full and lightweight getattr, setattr, and reclaim.

Dependencies:
- Depends on DragonFly VFS `struct vop_ops` and `struct vop_*_args` declarations being available from including context.
- Uses `__read_mostly`, so it is tied to DragonFly kernel compiler/storage annotations.

Notable risks:
- This is a small internal interface; signature changes must match both the VOP table definitions and callers in tmpfs code.
- The header intentionally exposes only a narrow subset of tmpfs vnode operations, so additional tmpfs VOPs may be private to implementation files.
