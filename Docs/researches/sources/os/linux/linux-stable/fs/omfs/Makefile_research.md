# File Research: sources/os/linux/linux-stable/fs/omfs/Makefile

## Scope

This Makefile wires the OMFS module into the kernel build.

## Behavior

- Builds `omfs.o` when `CONFIG_OMFS_FS` is enabled.
- The module is composed from `bitmap.o`, `dir.o`, `file.o`, and `inode.o`.

## Dependencies

- Mirrors the implementation split: allocation bitmap, directory operations, file extent/page-cache operations, and inode/superblock/module lifecycle.
