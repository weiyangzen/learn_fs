# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_io.c

## Purpose
Implements scratch-buffer read/free support shared by kernel and userland V7FS core code.

## Main Interfaces
- `scratch_read()` reads a block into either one of the static per-mount scratch buffers in kernel builds or a newly allocated userland buffer.
- `scratch_free()` releases the selected scratch slot or frees the userland buffer.
- `scratch_remain()` reports remaining static scratch buffers in kernel builds.

## Implementation Notes
Kernel builds use `STATIC_BUFFER` and `MEM_LOCK()` to manage three fixed scratch blocks. Userland builds allocate one `V7FS_BSIZE` buffer per read. Scratch exhaustion asserts in kernel mode.

## Dependencies
Depends on `struct v7fs_self`, the block I/O `read` callback, and lock macros from `v7fs_impl.h`.
