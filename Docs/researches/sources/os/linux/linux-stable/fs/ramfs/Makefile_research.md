# File Research: sources/os/linux/linux-stable/fs/ramfs/Makefile

## Purpose
Build rules for ramfs.

## Behavior
- Always builds `ramfs.o` into `obj-y`.
- `ramfs-objs` consists of `inode.o` plus either:
  - `file-mmu.o` when `CONFIG_MMU=y`,
  - `file-nommu.o` otherwise.

## Role
Selects the correct ramfs file operation implementation for MMU vs no-MMU kernels.
