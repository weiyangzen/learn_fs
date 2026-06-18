# File Research: sources/os/linux/linux-stable/fs/bfs/inode.c

This file implements BFS mount, inode read/write/evict, statfs, inode cache, filesystem registration, and superblock scanning.

Exports:
- `bfs_iget()`
- `bfs_dump_imap()`

Inode flow:
- `bfs_iget()` validates inode number, reads the inode table block, reconstructs Linux mode from BFS `i_vtype` plus low permission bits, assigns directory or regular-file operations, populates block range, uid/gid, link count, size, block count, and timestamps.
- `find_inode()` locates an on-disk inode and returns the backing buffer.
- `bfs_write_inode()` writes VFS inode state back to disk, including type, mode, owner, nlink, timestamps, start/end blocks, and end offset, with optional synchronous buffer write.
- `bfs_evict_inode()` truncates pages, syncs/invalidates metadata buffers, clears on-disk inode for unlinked files, releases inode/block bitmap accounting, and adjusts `si_lf_eblk`.

Superblock flow:
- `bfs_fill_super()` allocates `bfs_sb_info`, sets BFS block size, reads and validates the superblock magic and start/end fields, computes `si_lasti`, initializes reserved inode bits, loads root inode, computes block/free counts, verifies the final block is readable, scans all inode table entries for corruption, builds the inode bitmap, subtracts used file blocks, and tracks the highest end block.
- `bfs_statfs()` reports block/inode availability.
- `bfs_put_super()` destroys the mutex and frees private state.

Registration:
- Defines slab cache allocation/free for `bfs_inode_info`.
- `bfs_fs_type` uses fs_context with `get_tree_bdev()`.
- Module init creates the cache and registers the filesystem.

Integration:
- Directory and file layers depend on `bfs_iget()` and private inode state.
- Uses fixed on-disk definitions from `<linux/bfs_fs.h>`.
- Uses `mapping_metadata_bhs` initialization for metadata fsync support.

Risk notes:
- Mount continues on unclean BFS filesystems after logging a warning.
- The corruption scan validates inode block ranges and offsets, but skipped unreadable inode-table blocks during scan can leave holes.
- The filesystem is writable but simple; consistency depends on the global mutex and synchronous metadata paths.
