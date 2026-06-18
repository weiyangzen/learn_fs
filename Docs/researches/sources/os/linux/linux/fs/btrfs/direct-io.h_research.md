# File Research: sources/os/linux/linux/fs/btrfs/direct-io.h

This header declares the Btrfs direct I/O entry points and bioset lifecycle.

Exported API:
- `btrfs_init_dio()` initializes direct I/O bio allocation state.
- `btrfs_destroy_dio()` releases direct I/O bio allocation state.
- `btrfs_direct_write()` handles direct write requests from the file write path, with buffered fallback where required.
- `btrfs_direct_read()` handles direct read requests from the file read path, with validation behavior that lets callers fall back when direct I/O is unsuitable.

Design notes:
- The header forward declares `struct kiocb`; `struct iov_iter` is referenced by the prototypes through kernel headers included by translation units using this header.
- The implementation depends on iomap, Btrfs ordered extents, Btrfs bios, and delalloc reservation helpers.
