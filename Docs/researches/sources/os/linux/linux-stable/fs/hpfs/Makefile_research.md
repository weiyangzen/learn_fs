# File Research: sources/os/linux/linux-stable/fs/hpfs/Makefile

## Purpose

Build rules for the HPFS filesystem module.

## Build Behavior

Builds `hpfs.o` when `CONFIG_HPFS_FS` is enabled. The object is composed of allocation, anode, buffer, dentry, directory, dnode, EA, file, inode, map, name, namei, and superblock source files.

## Risks

The object list captures the filesystem’s subsystem boundaries. Omitting any component would break exported operations referenced through `hpfs_fn.h`.
