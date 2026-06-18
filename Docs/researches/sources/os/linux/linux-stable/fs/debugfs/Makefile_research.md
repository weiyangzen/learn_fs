# File Research: sources/os/linux/linux-stable/fs/debugfs/Makefile

## Purpose

Builds the debugfs filesystem object when `CONFIG_DEBUG_FS` is enabled.

## Main Responsibilities

- Defines `debugfs-objs` as `inode.o file.o`.
- Adds `debugfs.o` to the build through `obj-$(CONFIG_DEBUG_FS)`.

## Dependencies

- Controlled entirely by the kernel `CONFIG_DEBUG_FS` option.
- Combines debugfs inode/mount logic from `inode.c` with file helper/proxy logic from `file.c`.
