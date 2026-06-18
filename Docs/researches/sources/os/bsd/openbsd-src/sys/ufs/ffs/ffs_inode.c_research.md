# File Research: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_inode.c

Implements FFS inode metadata updates and truncation, including recursive indirect block freeing.

Key entry points:
- `ffs_update()` writes a UFS1/UFS2 inode to disk and updates timestamps.
- `ffs_truncate()` grows or shrinks files/directories/symlinks and frees blocks/fragments.
- `ffs_indirtrunc()` recursively clears and frees indirect block trees.

Important behavior:
- `ffs_update()` handles old UFS1 uid/gid compatibility fields and asserts effective link count matches disk link count.
- `ffs_truncate()` obtains inode quota state, enforces `fs_maxfilesize`, updates UVM size, and resets clustering state.
- Shrink writes the shortened inode and block pointers before freeing blocks.
- Unlike ext2, FFS handles fragment shrinkage of the final direct block and returns quota blocks through `ufs_quota_free_blocks()`.
- Direct block freeing uses `blksize()` so partial final fragments are accounted correctly.
- `ffs_indirtrunc()` supports UFS1 32-bit and UFS2 64-bit block pointer arrays through `BAP` macros.

Dependencies:
- Uses `UFS_BUF_ALLOC`, `UFS_UPDATE`, `ffs_blkfree()`, quota helpers, buffer cache, and UFS/FFS geometry macros.

Watch points:
- Triple indirect blocks are noted as untested.
- The code relies on writing pointer-cleared metadata before freeing storage to preserve fsck recoverability after crashes.
