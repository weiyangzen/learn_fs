# File Research: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_fifoops.h

Kernel-only declaration header for tmpfs FIFO vnode operations.

Key responsibilities:
- Enforces kernel-only inclusion.
- Includes generic tmpfs vnode operation declarations.
- Declares the external FIFO vnode operation vector `tmpfs_fifoop_entries`.

Dependencies:
- `fs/tmpfs/tmpfs_vnops.h` for shared tmpfs vnode operation declarations.

Notable risks:
- This header is intentionally small but is part of the vnode operation wiring for FIFO nodes allocated in tmpfs.
