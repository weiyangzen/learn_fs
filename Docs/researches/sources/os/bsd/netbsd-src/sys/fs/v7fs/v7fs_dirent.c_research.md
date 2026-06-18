# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_dirent.c

## Purpose
Provides directory-entry endian conversion and filename normalization for V7FS directory records.

## Main Interfaces
- `v7fs_dirent_endian_convert()` converts `inode_number` fields in an array of `struct v7fs_dirent` from on-disk order and checks inode-number sanity.
- `v7fs_dirent_filename()` truncates and NUL-pads names to `V7FS_NAME_MAX + 1` for stable comparisons.

## Implementation Notes
Directory names are fixed-width V7 names; lookups compare the normalized buffer with `strncmp(..., V7FS_NAME_MAX)`. The conversion function returns `false` if it sees invalid inode numbers, while still writing converted inode numbers into the records.

## Dependencies
Depends on superblock inode bounds via `v7fs_inode_number_sanity()` and endian macros from `v7fs_endian.h`.
