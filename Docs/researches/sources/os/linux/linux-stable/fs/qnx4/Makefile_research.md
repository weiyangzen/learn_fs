# File Research: sources/os/linux/linux-stable/fs/qnx4/Makefile

## Summary
Build rules for the QNX4 filesystem module.

## Main Responsibilities
- Build `qnx4.o` when `CONFIG_QNX4FS_FS` is enabled.
- Compose the module from `inode.o`, `dir.o`, `namei.o`, and `bitmap.o`.

## Cross-File Interactions
The listed objects implement mount/inode/block mapping, directory iteration, lookup, and free-block counting.
