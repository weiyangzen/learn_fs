# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_dirent.h

## Purpose
Declares directory-entry utilities used by lookup, readdir, rename, and directory mutation code.

## Main Interfaces
- `v7fs_dirent_endian_convert()` for batch conversion and validation of directory entries.
- `v7fs_dirent_filename()` for fixed-length V7 filename normalization.

## Dependencies
Requires V7FS directory-entry definitions and `struct v7fs_self` from the surrounding V7FS headers.
