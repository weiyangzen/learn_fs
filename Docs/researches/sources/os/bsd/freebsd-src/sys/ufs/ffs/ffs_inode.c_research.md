# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_inode.c

FFS inode update and truncation logic.

Key responsibilities:
- `ffs_update()` writes in-core inode state back to the inode block, after `ufs_itimes()` applies access/modify/change timestamps.
- It tracks durable-size/block-pointer changes using `IN_SIZEMOD` and `IN_IBLKDATA`, clearing them only on synchronous inode writes so `fsync()`/`fdatasync()` semantics remain correct.
- Snapshot inode updates avoid deadlock by using `GB_LOCK_NOWAIT`; if the inode buffer is busy, the code temporarily drops the vnode lock, waits, relocks, and revalidates the vnode.
- UFS1 and UFS2 inode writes copy the correct dinode format into the inode block; UFS2 updates dinode check hashes before writing.
- `ffs_truncate()` handles file growth, shrink, full truncation, external attribute truncation, short symlink clearing, directory hash truncation, page/buffer invalidation, quota adjustment, and block freeing.
- Growth path sets VM object size, allocates the last byte via `UFS_BALLOC`, writes the buffer, updates inode size, and writes the inode.
- Shrink path ensures the final block exists when needed, zeros partial-block tail data for non-directories, writes the shortened inode before freeing old blocks, then restores old pointers in memory temporarily to walk and release obsolete storage.
- Soft updates fast path can delegate zero-length truncation to `softdep_setup_freeblocks()` or journal freeblocks; otherwise truncation falls back to synchronous cleanup.
- Extended-attribute data on UFS2 can be truncated separately via `IO_EXT`, including slow synchronous freeing when soft updates cannot cover it.
- `ffs_indirtrunc()` recursively frees indirect-block trees in LIFO order, first zeroing entries and writing the indirect block so crash recovery sees the shortened tree before old blocks are released.
- `ffs_rdonly()` reports filesystem read-only state from the inode’s filesystem.

Important patterns:
- Inode/block pointer updates are persisted before block frees to preserve crash consistency.
- TRIM aggregation is used for freeing runs of direct and indirect blocks.
- `vtruncbuf()` and `vn_pages_remove()` keep buffer cache and VM object state aligned with new file size.
- Invariant checks verify final direct/indirect pointers match the shortened configuration and that full truncation leaves no buffers.

Research relevance:
- This file is central to FFS durability semantics: timestamp writeback, inode persistence, truncation ordering, soft updates interaction, and recursive indirect-block cleanup.
