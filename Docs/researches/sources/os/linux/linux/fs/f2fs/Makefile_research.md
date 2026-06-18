# File Research: sources/os/linux/linux/fs/f2fs/Makefile

## Purpose
Defines the F2FS composite kernel object and optional object inclusion.

## Object Composition
- Core `f2fs-y`: `dir.o`, `file.o`, `inode.o`, `namei.o`, `hash.o`, `super.o`, `inline.o`, `checkpoint.o`, `gc.o`, `data.o`, `node.o`, `segment.o`, `recovery.o`, `shrinker.o`, `extent_cache.o`, `sysfs.o`.
- Optional objects:
  - `debug.o` for `CONFIG_F2FS_STAT_FS`
  - `xattr.o` for `CONFIG_F2FS_FS_XATTR`
  - `acl.o` for `CONFIG_F2FS_FS_POSIX_ACL`
  - `verity.o` for `CONFIG_FS_VERITY`
  - `compress.o` for `CONFIG_F2FS_FS_COMPRESSION`
  - `iostat.o` for `CONFIG_F2FS_IOSTAT`
