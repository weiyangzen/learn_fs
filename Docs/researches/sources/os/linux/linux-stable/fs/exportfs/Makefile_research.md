# File Research: sources/os/linux/linux-stable/fs/exportfs/Makefile

## Summary
Builds the generic exportfs support object when `CONFIG_EXPORTFS` is enabled.

## Main Contents
- Adds `exportfs.o` to the kernel build for `CONFIG_EXPORTFS`.
- Defines `exportfs-objs := expfs.o`.

## Risks
This file is simple build glue. Its only behavioral significance is that all exportfs code in this directory currently comes from `expfs.c`.
