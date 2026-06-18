# File Research: sources/os/linux/linux/fs/bfs/Makefile

## Purpose
Build file for the BFS filesystem driver.

## Build Rules
- `obj-$(CONFIG_BFS_FS) += bfs.o`
- `bfs-objs := inode.o file.o dir.o`

## Research Notes
The BFS module is composed of three implementation files: superblock/inode handling, file data/block mapping, and directory operations.
