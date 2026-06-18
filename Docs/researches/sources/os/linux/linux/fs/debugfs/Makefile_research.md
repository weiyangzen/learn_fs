# File Research: sources/os/linux/linux/fs/debugfs/Makefile

## Role

Build definition for debugfs.

## Behavior

- Builds `debugfs.o` when `CONFIG_DEBUG_FS` is enabled.
- Composes `debugfs.o` from:
  - `inode.o`
  - `file.o`

## Research Notes

This makefile confirms that debugfs in this tree is split between inode/mount/lifecycle code in `inode.c` and file-operation helper/proxy code in `file.c`.
