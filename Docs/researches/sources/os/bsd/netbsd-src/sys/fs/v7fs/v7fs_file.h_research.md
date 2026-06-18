# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_file.h

## Purpose
Declares core and utility-level V7FS file/directory operations.

## Main Interfaces
- `struct v7fs_lookup_arg` is the shared callback context for name lookup, inode-number lookup, replacement, and removal.
- Declares allocation/deallocation, directory add/remove, rename, replacement, link, lookup-by-number, and symlink helpers.

## Dependencies
Requires `struct v7fs_self`, `struct v7fs_inode`, `struct v7fs_fileattr`, and V7FS inode/address typedefs from core headers.
