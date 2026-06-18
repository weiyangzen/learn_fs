# File Research: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_io.c

Tarfs backing-file I/O and optional zstd decompression layer, including a synthetic vnode used to expose the decompressed byte stream internally.

Key responsibilities:
- Defines debug-only decompression sysctls and counters for inflated, consumed, and bounced bytes, plus a reset handler.
- Defines allocator hooks for zstd decompression state when `ZSTDIO` is compiled in.
- Implements `tarfs_io_read()` to read either the raw backing vnode or the decompressed synthetic znode, applying vnode range locks and vnode locks as needed.
- Implements `tarfs_io_read_buf()` for kernel-buffer reads using a one-element `uio`.
- Detects archive compression signatures for xz, gzip/zlib, and zstd; only zstd is supported when `ZSTDIO` is enabled, while xz and zlib return `EOPNOTSUPP`.
- Maintains a decompression frame index mapping compressed input offsets to decompressed output offsets, allowing zstd stream reset/skip for backward or far-forward reads.
- Implements znode vnode operations: read-only access delegation to the backing vnode, synthesized attributes, zstd-backed reads, reclaim cleanup, and strategy reads into buffers.
- Implements `tarfs_zread_zstd()` with input buffering, optional user-space bounce buffer, stream reset, frame-boundary indexing, EOF/error detection, and counter updates.
- Creates the synthetic znode in `tarfs_zio_init()` with inode `TARFS_ZIOINO` and operation vector `tarfs_znodeops`.
- Tears down znode, zstd stream, index, and zio allocation in `tarfs_io_fini()`.

Dependencies:
- FreeBSD vnode locking, range locking, `VOP_READ`, `VOP_GETATTR`, buffer strategy, sysctl, counter, malloc, and UIO APIs.
- Optional in-kernel zstd library through `contrib/zstd/lib/zstd.h`.
- Tarfs mount fields `vp`, `znode`, `zio`, `iosize`, `root`, and debug macros.

Notable risks:
- Decompression is stateful and serialized by taking the znode lock exclusively for non-raw reads.
- Random access before the current decompressed position requires stream reset to the nearest recorded frame index; indexing quality affects performance.
- Non-kernel-space reads allocate a full-length bounce buffer, which can be expensive for large reads.
- Error paths reset zstd state and current index to the first entry to recover from failed decompression.
- xz and zlib magic are detected but unsupported despite a module dependency on xz elsewhere.
