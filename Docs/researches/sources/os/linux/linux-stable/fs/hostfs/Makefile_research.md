# File Research: sources/os/linux/linux-stable/fs/hostfs/Makefile

## Purpose

Build rules for UML hostfs.

## Build Behavior

`hostfs.o` is built from `hostfs_kern.o`. When `CONFIG_HOSTFS` is enabled, `hostfs_user.o` and `hostfs_user_exp.o` are included in built-in hostfs objects. The file includes `arch/um/scripts/Makefile.rules`, reflecting that hostfs is specific to User-Mode Linux.

## Risks

The split between kernel-facing hostfs code and UML userspace syscall wrappers is build-system dependent. Moving these objects outside UML rules would break symbol availability.
