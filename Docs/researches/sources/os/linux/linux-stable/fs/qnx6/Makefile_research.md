# File Research: sources/os/linux/linux-stable/fs/qnx6/Makefile

## Summary
Build rules for the QNX6 filesystem module.

## Main Responsibilities
- Build `qnx6.o` when `CONFIG_QNX6FS_FS` is enabled.
- Compose the module from `inode.o`, `dir.o`, `namei.o`, and `super_mmi.o`.
- Add debug compiler flags when `CONFIG_QNX6FS_DEBUG` is enabled.

## Cross-File Interactions
The objects cover mount/inode/block mapping, directory iteration/search, lookup, and MMI superblock handling.
