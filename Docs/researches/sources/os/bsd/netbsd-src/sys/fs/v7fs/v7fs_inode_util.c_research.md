# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_inode_util.c

## Purpose
Provides inode utility routines for chmod, diagnostic dumping, and walking every inode in the ilist.

## Main Interfaces
- `v7fs_inode_chmod()` replaces only permission bits while preserving file type bits.
- `v7fs_inode_dump()` prints inode metadata and special-device major/minor information.
- `v7fs_ilist_foreach()` reads every ilist sector, converts each disk inode to memory form, and invokes a callback.

## Dependencies
Uses scratch I/O, `v7fs_inode_setup_memory_image()`, superblock ilist bounds, and optional userland time formatting.
