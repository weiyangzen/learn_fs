# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_endian.c

## Purpose
Implements V7FS endian conversion, including the 24-bit disk block address packing used by V7 inodes.

## Main Interfaces
- `v7fs_endian_init()` installs per-mount conversion callbacks when `V7FS_EI` is enabled.
- `val24_normal_order_read()` and `val24_normal_order_write()` always provide native-order 24-bit address packing/unpacking.

## Implementation Notes
The optional endian-independent path supports little, big, and PDP endian modes. PDP conversion is handled specially for 32-bit values and 24-bit addresses. Without `V7FS_EI`, the macros in the header are pass-through except for normal 24-bit helpers.

## Dependencies
Uses `<sys/endian.h>`, mount-level `fs->endian`, and callback storage in `struct endian_conversion_ops`.
