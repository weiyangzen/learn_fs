# File Research: sources/os/linux/linux-stable/fs/kernfs/Makefile

## Purpose

Builds kernfs core objects into the kernel when the directory is included.

## Objects

`obj-y` includes `mount.o`, `inode.o`, `dir.o`, `file.o`, and `symlink.o`. The researched `dir.c` is one component of the kernfs pseudo-filesystem implementation.
