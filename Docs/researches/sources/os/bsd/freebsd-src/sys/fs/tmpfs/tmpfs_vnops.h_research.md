# File Research: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_vnops.h

Kernel-only declaration header for FreeBSD tmpfs vnode operations.

Key responsibilities:
- Guards against userland inclusion.
- Declares the main tmpfs VOP vectors: `tmpfs_vnodeop_entries` and `tmpfs_vnodeop_nonc_entries`.
- Publishes shared tmpfs VOP entry points used outside `tmpfs_vnops.c`: access, fast lookup execute check, stat, getattr, setattr, pathconf, print, and reclaim.

Dependencies:
- Requires kernel VFS operation typedefs such as `vop_access_t`, `vop_getattr_t`, and `struct vop_vector`.

Notable risks:
- Signature or exported symbol changes must stay synchronized with `tmpfs_vnops.c` and other tmpfs implementation files.
- The header intentionally exposes only a narrow internal interface; most VOPs remain private to the implementation file.
