# File Research: sources/os/linux/linux-stable/fs/hpfs/inode.c

## Purpose

Implements HPFS inode initialization, fnode-to-inode loading, inode writeback, setattr, dirty flush, and eviction.

## Main Entry Points

- `hpfs_init_inode()`
- `hpfs_read_inode()`
- `hpfs_write_inode()` / `hpfs_write_inode_nolock()`
- `hpfs_setattr()`
- `hpfs_write_if_changed()`
- `hpfs_evict_inode()`

## Control Flow And State

Inode initialization applies mount default uid/gid/mode and clears HPFS-private caches. Reading an inode maps its fnode, optionally reads EAs for UID/GID/SYMLINK/MODE/DEV, initializes special files or symlinks from EAs, and otherwise configures directory or regular-file operations. Directories count dnodes/subdirectories for size/link count; files set size and address-space ops from the fnode.

Writeback finds the parent directory entry through the fnode and updates file size, times, read-only flag, EA size, and mode/uid/gid/device EAs when EA write support is enabled. `setattr` forbids growing files, validates 16-bit uid/gid limits, truncates on shrink, and writes metadata. Eviction removes fnodes for unlinked inodes.

## Dependencies

Uses fnode mapping, EA helpers, directory search helpers, file/directory/symlink operations, time conversion, and global HPFS locking.

## Risks

HPFS stores Unix metadata in optional EAs, so behavior depends on the `eas` mount mode. Root inode writeback is skipped. File growth through setattr is rejected; normal writes grow through the file block allocator.
