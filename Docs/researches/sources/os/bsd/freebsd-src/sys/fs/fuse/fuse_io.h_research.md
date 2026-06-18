# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_io.h

This header declares the FUSE I/O backend API implemented by `fuse_io.c`.

Declared functions:
- `fuse_io_strategy`: buffer-cache strategy path for `BIO_READ` and `BIO_WRITE`.
- `fuse_io_flushbuf`: flushes vnode buffers.
- `fuse_io_invalbuf`: flushes and invalidates vnode buffers.
- `fuse_read_directbackend`: sends direct `FUSE_READ` operations into a caller `uio`.
- `fuse_read_biobackend`: services reads through FreeBSD buffer-cache helpers.
- `fuse_write_directbackend`: sends direct `FUSE_WRITE` operations from a caller `uio`.
- `fuse_write_biobackend`: services writes through FreeBSD buffer-cache helpers.

Integration points:
- Consumers are vnode read/write/strategy and invalidation paths.
- The signatures expose `struct fuse_filehandle`, credentials, I/O flags, pid, file size, and page/writeback-origin information needed to preserve FUSE protocol behavior.

Notable risks and research hooks:
- Callers must pass the correct file handle and cache/direct flags; the implementation assumes those choices were made correctly by upper vnode/file-handle code.
- `fuse_write_directbackend` needs the current file size from caller, making stale size inputs a possible cache-coherency concern.
