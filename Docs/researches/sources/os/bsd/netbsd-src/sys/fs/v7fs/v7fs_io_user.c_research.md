# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_io_user.c

## Purpose
Provides the userland V7FS block I/O implementation for tools/tests using file descriptors.

## Main Interfaces
- `v7fs_io_init()` allocates `struct v7fs_self`, stores fd/block-size/size state, initializes endian conversion, and chooses mmap or lseek/read/write callbacks.
- `v7fs_io_fini()` unmaps, fsyncs, and frees the V7FS runtime.
- `read_sector()`/`write_sector()` perform positioned fd I/O.
- `read_mmap()`/`write_mmap()` copy to/from the mapped device image.

## Implementation Notes
The attempted mmap uses `MAP_SHARED` and falls back to sector I/O on failure. A single static `local` I/O state is used.

## Dependencies
Uses POSIX file, mmap, fsync, and warning APIs plus V7FS endian/core headers.
