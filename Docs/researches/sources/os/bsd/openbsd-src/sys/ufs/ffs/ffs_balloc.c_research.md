# File Research: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_balloc.c

Allocates physical storage for logical file offsets, including direct blocks, fragments, and indirect trees.

Key entry points:
- `ffs_balloc()` dispatches to UFS2 or UFS1 implementation.
- `ffs1_balloc()` implements UFS1 allocation.
- `ffs2_balloc()` implements UFS2 allocation under `FFS2`.

Important behavior:
- Direct blocks may be full blocks or fragments depending on file size.
- When a write skips beyond a final fragment, the old fragment is extended to a full block first.
- For new indirect blocks, the code writes zeroed indirect blocks synchronously before linking parent pointers, avoiding pointers to garbage.
- Allocation failure after partial indirect allocation triggers an unwind path: fsync, clear parent pointer, free newly allocated blocks, restore quota, adjust block counts, and fsync again.
- `B_CLRBUF` controls whether returned buffers are cleared before use.

Dependencies:
- Uses `ufs_getlbns()` for indirect path decomposition.
- Uses `ffs_alloc()`, `ffs_realloccg()`, `ffs_blkfree()`, `ffs1_blkpref()`, `ffs2_blkpref()`, buffer cache, quota rollback, and UVM vnode size updates.

Watch points:
- Failure unwind is deliberately slow but protects against dangling softdep/block dependencies.
- UFS1 and UFS2 code are nearly parallel but differ in pointer width and some unwind details.
