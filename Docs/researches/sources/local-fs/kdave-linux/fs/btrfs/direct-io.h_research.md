# File Research: sources/local-fs/kdave-linux/fs/btrfs/direct-io.h

This header exposes Btrfs direct I/O lifecycle and read/write entry points.

Declared API:
- `btrfs_init_dio()` initializes the direct-I/O bioset.
- `btrfs_destroy_dio()` destroys the bioset.
- `btrfs_direct_write()` handles direct write requests and buffered fallback.
- `btrfs_direct_read()` handles direct read requests and signals fallback by returning 0 in unsupported cases.

Design notes:
- Only forward declares `struct kiocb`; the iov iterator type is used in prototypes through included kernel headers.
- The implementation details are kept private in `direct-io.c`, including iomap ops, bio private state, and locking behavior.
