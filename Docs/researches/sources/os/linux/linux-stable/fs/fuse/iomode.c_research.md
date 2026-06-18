# File Research: sources/os/linux/linux-stable/fs/fuse/iomode.c

## Purpose
Coordinates mutually exclusive FUSE inode I/O modes: cached page-cache use, uncached direct/passthrough use, and backing-file passthrough. It prevents unsafe mixing of cached and uncached access.

## Key Interfaces
- `fuse_file_cached_io_open()` enters cached I/O mode.
- `fuse_inode_uncached_io_start()` and `fuse_inode_uncached_io_end()` manage uncached mode references.
- `fuse_file_io_open()` validates server open flags and selects cached, direct, or passthrough mode.
- `fuse_file_io_release()` drops the per-file mode reference.

## Control Flow And Behavior
Cached opens increment `fi->iocachectr` and set `FUSE_I_CACHE_IO_MODE`; uncached users decrement the same counter. Negative values represent active uncached users, positive values cached users. Cached opens wait for parallel direct I/O writers to drain unless the inode has entered passthrough mode.

Passthrough opens require `CONFIG_FUSE_PASSTHROUGH`, connection passthrough support, and a restricted set of open flags. A backing file ID is resolved and installed, then uncached mode is acquired so the FUSE page cache cannot coexist with passthrough.

## Dependencies
Uses `struct fuse_inode`, `struct fuse_file`, backing-file lookup/release from FUSE passthrough/backing code, inode spin locks, wait queues, and FUSE open flags.

## Risks And Invariants
A server must consistently use `FOPEN_PASSTHROUGH` once an inode has a backing file. `FOPEN_PARALLEL_DIRECT_WRITES` is only meaningful with `FOPEN_DIRECT_IO`. Conflicting cached and passthrough/uncached users fail with user-visible `EIO` after logging a debug message.
