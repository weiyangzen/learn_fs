# File Research: sources/os/linux/linux/fs/ufs/ialloc.c

Purpose: UFS inode allocation and freeing.

Key behavior:
- `ufs_free_inode()` validates inode number, loads its cylinder group, clears the inode bitmap bit, updates free inode and directory counts, marks buffers/superblock dirty, and syncs if needed.
- `ufs2_init_inodes_chunk()` zeroes a newly initialized UFS2 inode chunk and advances `cg_initediblk`.
- `ufs_new_inode()` allocates a new VFS inode and on-disk inode number:
  - rejects creation in deleted directories
  - prefers parent cylinder group
  - uses quadratic then linear search for free inodes
  - sets inode bitmap bit and updates cylinder/superblock counters
  - initializes VFS inode owner, times, flags, UFS private state, and inserts inode
  - for UFS2, writes birth time into the on-disk inode immediately

Integration:
- Called by UFS namespace creation paths.
- Uses cylinder group cache from `cylinder.c`, superblock geometry, and UFS bitmap helpers.

Risks and invariants:
- `ufs_free_inode()` comments emphasize clearing VFS inode state before bitmap reuse to avoid aliasing.
- Global UFS superblock lock protects inode bitmap and counter changes.
- UFS2 lazy inode initialization occurs when allocation crosses initialized inode blocks.
