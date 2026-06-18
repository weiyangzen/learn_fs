# File Research: sources/os/bsd/dragonflybsd/sys/sys/_uio.h

Read completely: 76 lines.

This kernel-only header defines the `uio` transfer descriptor.

Key contents:
- `enum uio_rw`: `UIO_READ`, `UIO_WRITE`.
- `enum uio_seg`: user-space, system-space, and no-copy segment modes.
- Forward declarations for `iovec` and `thread`.
- `struct uio` with iovec pointer/count, offset, residual byte count, segment flag, read/write direction, and associated thread.

Important interactions:
- Used heavily by vnode, device, and filesystem read/write paths, including `vfs_vnops.c`.

Security/reliability notes:
- Header is guarded to `_KERNEL`/`_KERNEL_STRUCTURES`.
- `uio_resid` is `size_t`, not signed, which affects overflow and completion checks in I/O code.
