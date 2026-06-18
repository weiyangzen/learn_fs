# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_impl.h

## Purpose
Defines V7FS implementation-private runtime structures, I/O callbacks, locking hooks, scratch buffers, mount-device inputs, stats, and iterator sentinel codes.

## Main Interfaces
- `struct block_io_ops` abstracts read/write of one or more disk sectors.
- `struct v7fs_self` is the core per-mount state: scratch buffers, I/O ops, optional endian ops, optional locks, superblock, stats, and endian selection.
- `struct v7fs_fileattr` carries create-time uid/gid/mode/device/timestamps.
- `SUPERB_LOCK`, `ILIST_LOCK`, and `MEM_LOCK` map to lock callbacks in kernel builds and no-ops otherwise.
- Declares `v7fs_io_init()`, `v7fs_io_fini()`, `scratch_read()`, `scratch_free()`, and `scratch_remain()`.

## Dependencies
Bridges kernel and userland builds with conditional locking, assertions, and scratch-buffer allocation policy.
