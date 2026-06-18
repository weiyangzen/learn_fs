# File Research: sources/local-fs/xfsprogs/libxfs/libxfs_io.h

Userspace libxfs buffer I/O interface definitions.

Key responsibilities:
- Defines `xfs_buftarg`, buffer target flags, write-failure injection, and flush interface.
- Defines `xfs_bufkey`, `xfs_buf_map`, `xfs_buf_ops`, and `xfs_buf`.
- Declares cached, uncached, mapped, read, write, release, lock, priority, delwri, flush, purge, and zeroing buffer APIs.
- Provides inline wrappers for single-map get/read and checksum update/verify helpers.
- Defines buffer flags and daddr conversion helpers.

Important behavior:
- Buffer verifiers carry read/write/structure callbacks.
- `xfs_buftarg_trip_write` can call `platform_crash` after configured writes.
- Memory-backed targets are represented via non-NULL `bt_xfile`.
- `xfs_buf_hold` increments the cache node refcount directly.

Dependencies:
- Shared by most libxfs code using buffers, devices, cache, transactions, and verifiers.

Notable risks:
- Direct refcount manipulation in inline helpers requires careful cache discipline.
- The userspace `xfs_buf` structure is a compatibility model, not the kernel buffer implementation.
