# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_balloc.c

This file implements FFS logical-block allocation for UFS1 and UFS2. It allocates direct blocks, indirect blocks, fragments, and UFS2 external attribute data blocks, using lower-level allocation routines from `ffs_alloc.c`.

Key responsibilities:
- Dispatch block allocation to UFS1 or UFS2 implementation.
- Allocate or grow direct blocks/fragments.
- Allocate indirect block chains safely.
- Ensure indirect blocks are written before pointers reference them.
- Support metadata-only allocation and UFS2 external data allocation.
- Unwind partial indirect allocations on failure.
- Run copy-on-write hooks for snapshot safety.

Important functions:
- `ffs_extb`: Reads a UFS2 external data block pointer with byte swapping.
- `ffs_balloc`: Dispatches to `ffs_balloc_ufs1` or `ffs_balloc_ufs2` based on superblock magic, then runs `fscow_run` on returned buffers.
- `ffs_balloc_ufs1`: UFS1 allocator. It computes logical block and requested block size, extends a prior final fragment to a full block when writing beyond it, handles direct blocks by reading existing blocks, growing fragments with `ffs_realloccg`, or allocating new blocks/fragments with `ffs_alloc`. For indirect blocks, it uses `ufs_getlbns`, allocates missing indirect blocks synchronously, updates indirect pointers, allocates data blocks, and unwinds allocations on failure.
- `ffs_balloc_ufs2`: UFS2 allocator. It mirrors UFS1 logic with 64-bit block pointers and additionally supports `IO_EXT` external data allocation using `di_extb` and `di_extsize`.

Important indirect-allocation behavior:
- Missing indirect blocks are allocated with `B_METAONLY`.
- Newly allocated indirect blocks are obtained zeroed and written synchronously before parent pointers are installed, preventing pointers to garbage.
- On failure after partial allocation, delayed-write buffers are flushed to resolve dependencies, parent pointers are cleared, created buffers are invalidated, allocated blocks are freed, quotas are restored, and inode block counts are decremented.

Important direct/external allocation behavior:
- Existing full blocks are simply read when a buffer is requested.
- Existing partial fragments are reused if large enough or grown with `ffs_realloccg`.
- New direct blocks allocate a fragment when the file does not yet cover the full logical block, otherwise a full block.
- UFS2 external data uses negative logical block numbers (`-1 - lbn`) for buffer-cache addressing.

Important interactions:
- Depends on `ffs_alloc`, `ffs_realloccg`, `ffs_blkfree`, `ffs_blkpref_ufs1`, `ffs_blkpref_ufs2`, `ffs_getblk`, `ufs_getlbns`, quota code, and snapshot copy-on-write via `fscow_run`.
- Updates inode size fields and UVM vnode size when extending the previous last fragment to a full block.

Notable behavior and risks:
- `ffs_balloc_ufs2` asserts that `IO_EXT` is only used when `UFS_EA` is enabled.
- Both UFS1 and UFS2 paths have complex unwind logic; correctness depends on `unwindidx`, `allocib`, and `allocblk` accurately tracking all newly allocated metadata/data blocks.
- The UFS2 path for extending the previous last fragment calls `ffs_getdb(fs, ip, lbn)` where the analogous UFS1 code uses `nb`; this asymmetry is worth checking if investigating allocation bugs.
