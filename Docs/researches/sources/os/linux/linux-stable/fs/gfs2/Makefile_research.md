# File Research: sources/os/linux/linux-stable/fs/gfs2/Makefile

## Purpose
Builds the `gfs2.o` composite object from GFS2 subsystem source files.

## Key Interfaces
- `obj-$(CONFIG_GFS2_FS) += gfs2.o`
- `gfs2-y` lists core GFS2 implementation objects.
- `gfs2-$(CONFIG_GFS2_FS_LOCKING_DLM)` conditionally adds `lock_dlm.o`.

## Design Notes
Adds `-I$(src)` include flags and composes the filesystem from ACL, block mapping, directory, xattr, glock, log, inode, quota, rgrp, superblock, transaction, and utility modules.

## Dependencies
Driven by Kbuild and the Kconfig symbols in the same directory.
