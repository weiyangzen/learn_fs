# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_balloc.c

FFS logical-to-physical block allocation routine for file writes.

Key responsibilities:
- Implements `ffs_balloc`, the VOP balloc entry point that ensures storage exists for a requested vnode byte range and returns the corresponding buffer.
- Validates logical block number, requested size, and exclusive vnode locking.
- Extends a prior EOF fragment to a full block when a write moves into later blocks.
- Handles direct blocks, including existing full blocks, existing fragments that may need reallocation, and newly allocated fragments/full blocks.
- For indirect blocks, computes the indirection chain with `ufs_getlbns`, pre-acquires the data buffer to avoid VM/filesystem deadlocks, allocates missing indirect blocks synchronously or with soft updates metadata dependencies, and allocates the final data block.
- Honors `B_CLRBUF`, `B_SYNC`, clustering, asynchronous writes, and read-before-write behavior for existing uncached blocks.
- Maintains undo history for newly allocated indirect/data blocks and unwinds allocations on failure with fsync, buffer invalidation, quota rollback, inode block count adjustment, pointer clearing, and block frees.

Dependencies:
- Uses FFS allocation helpers `ffs_alloc`, `ffs_realloccg`, `ffs_blkpref`, and `ffs_blkfree`.
- Uses UFS block mapping helper `ufs_getlbns`, inode/block layout macros, buffer-cache APIs, cluster read, soft updates setup hooks, and quota accounting.

Notable risks:
- Failure cleanup is deliberately complex; missing an allocated block in the undo lists would leak space or leave dangling metadata.
- The code relies on exclusive vnode locking to safely modify inode direct and indirect block pointers.
- Indirect block allocation must not expose garbage pointers; synchronous metadata writes are used when soft updates is not active.
- `B_CLRBUF` behavior must preserve valid dirty data around truncation/extension edge cases.
