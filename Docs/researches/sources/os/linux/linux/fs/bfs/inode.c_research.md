# File Research: sources/os/linux/linux/fs/bfs/inode.c

## Purpose
Implements BFS superblock operations, inode load/write/evict, mount, statfs, inode cache, and module registration.

## Inode Loading
- `bfs_iget()`:
  - validates inode number range
  - reads the inode table block
  - reconstructs Linux mode from disk `i_mode` lower bits and `i_vtype`
  - assigns directory or regular-file operations
  - loads contiguous block range, disk inode number, uid/gid, link count, size, block count, and timestamps

## Disk Inode Access
- `find_inode()` validates inode number, reads the inode table block, and returns a pointer to the on-disk inode inside the buffer.

## Inode Writeback
- `bfs_write_inode()`:
  - serializes under BFS mutex
  - writes vtype, inode number, mode, ownership, links, timestamps, block range, and end offset
  - syncs buffer for `WB_SYNC_ALL`

## Eviction
- `bfs_evict_inode()`:
  - truncates page cache
  - syncs or invalidates tracked metadata buffers
  - clears inode
  - for deleted inodes, zeroes disk inode, frees data blocks/inode bitmap bit, and adjusts `si_lf_eblk` if this was the last file

## Superblock and Statfs
- `bfs_put_super()` destroys mutex and frees private info.
- `bfs_statfs()` reports magic, block size, total/free blocks, total/free files, fsid, and name length.
- `bfs_sops` wires inode allocation/free, write, eviction, put_super, and statfs.

## Mount Path
- `bfs_fill_super()`:
  - allocates and initializes `bfs_sb_info`
  - sets block size to `BFS_BSIZE`
  - reads and validates BFS superblock magic/ranges
  - warns on unclean filesystem
  - computes `si_lasti`, handling the practical maximum inode warning
  - initializes reserved inode bits
  - loads root inode and root dentry
  - computes total/free blocks
  - verifies last block is readable
  - scans the inode table to validate file block ranges, build inode bitmap, count free inodes, subtract used blocks, and find last allocated file block

## Filesystem Registration
- `bfs_fs_type` registers name `bfs`, block-device requirement, fs_context initialization, and `kill_block_super`.
- `init_bfs_fs()` creates inode cache and registers filesystem.
- `exit_bfs_fs()` unregisters and destroys cache.

## Research Notes
The mount scan performs important consistency checks before accepting the filesystem. BFS write support is present, but constrained by contiguous allocation and a simple global lock.
