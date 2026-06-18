# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_io_kern.c

## Purpose
Provides the kernel implementation of V7FS block I/O initialization, teardown, sector read/write, and mutex-backed lock callbacks.

## Main Interfaces
- `v7fs_io_init()` allocates `struct v7fs_self`, initializes endian conversion, I/O callbacks, local vnode/credential state, scratch state, and lock callbacks.
- `v7fs_io_fini()` frees local I/O state and destroys allocated mutexes.
- `v7fs_os_read()`/`v7fs_os_write()` use `bread()`, `getblk()`, and `bwrite()` for device-vnode sector I/O.
- `v7fs_os_read_n()`/`v7fs_os_write_n()` loop one sector at a time.

## Dependencies
Uses NetBSD vnode/buf/kmem/mutex APIs, `struct v7fs_mount_device`, and optional endian initialization.
