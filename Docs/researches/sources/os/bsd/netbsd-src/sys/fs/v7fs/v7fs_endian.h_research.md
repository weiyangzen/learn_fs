# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_endian.h

## Purpose
Defines the V7FS value-conversion macros used by superblock, inode, directory, and free-list code.

## Main Interfaces
- `V7FS_VAL32`, `V7FS_VAL16`, `V7FS_VAL24_READ`, and `V7FS_VAL24_WRITE` abstract disk/native conversion.
- `v7fs_endian_init()` is declared only for `V7FS_EI` builds.
- `val24_normal_order_read()` and `val24_normal_order_write()` are available in all builds.

## Dependencies
The `V7FS_EI` mode requires conversion callbacks in `struct v7fs_self`; the default mode assumes native on-disk order.
