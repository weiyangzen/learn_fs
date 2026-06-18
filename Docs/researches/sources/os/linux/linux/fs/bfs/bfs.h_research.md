# File Research: sources/os/linux/linux/fs/bfs/bfs.h

## Purpose
Private BFS driver header for in-core state, accessors, debug macro, and cross-file prototypes.

## Key Structures
- `struct bfs_sb_info`:
  - total blocks
  - free blocks/inodes
  - last file end block
  - last inode number
  - inode bitmap
  - global BFS mutex
- `struct bfs_inode_info`:
  - disk inode number
  - starting and ending data blocks
  - metadata buffer-head tracking for fsync
  - embedded VFS inode

## Constants
- `BFS_MAX_LASTI 513`: theoretical maximum last inode number, with comment explaining the practical root-directory limit that prevents using all 512 possible inodes.

## Helpers
- `BFS_SB()`
- `BFS_I()`
- `printf()` macro that logs with `BFS-fs` and function name.

## Exports
Declares BFS inode, file, address-space, and directory operation symbols shared across the three BFS source files.

## Research Notes
BFS uses a simple global mutex and contiguous file allocation model, reflected in the minimal private inode state.
