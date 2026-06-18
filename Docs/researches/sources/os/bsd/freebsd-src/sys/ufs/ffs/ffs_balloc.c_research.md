# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_balloc.c

FFS logical-block allocation implementation for UFS1 and UFS2. It maps a vnode file offset/logical block to allocated disk storage and returns the corresponding buffer.

Key responsibilities:
- `ffs_balloc_ufs1()` handles UFS1 file data allocation through direct blocks and single/double/triple indirect blocks.
- `ffs_balloc_ufs2()` mirrors that logic for UFS2 and additionally supports external attribute data via `IO_EXT` and `di_extb[]`.
- Both functions extend the previous final fragment to a full block when a later write would skip into a new block.
- Direct-block paths allocate or reallocate fragments/blocks, optionally clear invalid buffer contents (`BA_CLRBUF`), set buffer physical block numbers, update inode block pointers, and establish softdep direct/allocation dependencies.
- Indirect-block paths use `ufs_getlbns()` to walk indirect levels, allocate missing indirect blocks, initialize them, write them synchronously or asynchronously according to flags, and finally allocate the target data block.
- `BA_METAONLY` returns the indirect block buffer rather than allocating/fetching file data, used by truncation and snapshot code.
- Sequential reads through `BA_SEQMASK`/`BA_SEQSHIFT` may use `cluster_read()` when clearing/fetching existing blocks and memory pressure permits.
- Partial allocation failure unwinds allocated blocks: it syncs the vnode to remove dependencies, invalidates transient buffers, clears newly inserted pointers, restores quotas and inode block counts, syncs again, then frees the allocated blocks.
- UFS2 paths use unmapped buffers for metadata where appropriate and avoid WITNESS issues for snapshots via `GB_NOWITNESS`.

Important patterns:
- Every successful metadata pointer insertion sets inode flags such as `IN_CHANGE`, `IN_UPDATE`, and `IN_IBLKDATA`.
- `TDP_INBDFLUSH` is set while walking/allocating indirect blocks to avoid problematic recursive flushing behavior.
- Allocation failures under soft updates can request block cleanup once and retry before surfacing full-filesystem errors.
- UFS1 rejects `IO_EXT`; UFS2 treats external attributes as negative logical block numbers and marks buffers `BX_ALTDATA`.

Research relevance:
- This is the core bridge between VFS writes and FFS allocation policy.
- It shows how FFS builds direct/indirect block trees, integrates soft updates with block pointer publication, and preserves consistency during partial allocation failures.
