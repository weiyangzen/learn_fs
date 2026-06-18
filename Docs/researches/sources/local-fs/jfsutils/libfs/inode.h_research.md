# File Research: sources/local-fs/jfsutils/libfs/inode.h

## Purpose
Declares the inode read/write and disk-address lookup helpers implemented in `inode.c`.

## Interface
- `ujfs_rwinode(FILE *, struct dinode *, uint32_t, int32_t, int32_t, uint32_t, uint32_t)`
- `ujfs_rwdaddr(FILE *, int64_t *, struct dinode *, int64_t, int32_t, int32_t)`

## Dependencies
Includes `jfs_types.h` and `devices.h`; consumers must also have the JFS `struct dinode` definition available through included headers.

## Notes
This is a thin API header for shared libfs users that need to address aggregate or fileset inodes by number.
