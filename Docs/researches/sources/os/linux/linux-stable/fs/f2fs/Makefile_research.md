# File Research: sources/os/linux/linux-stable/fs/f2fs/Makefile

## Purpose
Defines F2FS object composition for the kernel build.

## Main Components
- Builds `f2fs.o` when `CONFIG_F2FS_FS` is enabled.
- Core objects include directory, file, inode, name lookup, hashing, superblock, inline data, checkpoint, GC, data, node, segment, recovery, shrinker, extent cache, and sysfs support.
- Optional objects are added for stats/debug, xattrs, POSIX ACLs, fs-verity, compression, and IO statistics.

## Research Notes
This file shows that `checkpoint.o` is core F2FS, while `acl.o` and `compress.o` are conditional feature objects.
