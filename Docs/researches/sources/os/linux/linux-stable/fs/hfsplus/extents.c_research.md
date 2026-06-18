# File Research: sources/os/linux/linux-stable/fs/hfsplus/extents.c

## Scope

Manages HFS+ extents in catalog records and the extents overflow B-tree, including block mapping, file extension, fork freeing, extent cache writeback/read, and truncation.

## APIs And Behavior

- `hfsplus_ext_cmp_key()` orders extents by CNID, fork type, then starting allocation block.
- `hfsplus_ext_write_extent()` flushes dirty cached overflow extents, inserting new records or overwriting existing records.
- `hfsplus_get_block()` maps VFS logical blocks to physical sectors, extends the file for sequential writes, resolves first or cached overflow extents, and marks the inode dirty when allocation or extent-cache writeback occurs.
- `hfsplus_free_fork()` frees first extents and overflow extents for a fork, removing overflow B-tree records as it walks backward.
- `hfsplus_file_extend()` checks allocation-file capacity, chooses an allocation goal from the last extent, allocates blocks from the bitmap with wraparound, optionally zeroes blocks, appends to first/cached extents, or starts a new overflow extent record.
- `hfsplus_file_truncate()` extends page-cache state when growing beyond physical size or frees extents/overflow records and updates physical/fs block counts when shrinking.

## State And Dependencies

Per-inode state includes first/cached extents, cached start/count, first block count, allocation blocks, clump blocks, physical size, filesystem blocks, and `HFSPLUS_EXT_DIRTY/NEW` state. The file depends on allocation bitmap routines, extents B-tree cursors, file write helpers, superblock allocation geometry, and inode/tree dirty flags.

## Risks And Invariants

The extents overflow tree is itself extent-backed, so `hfsplus_get_block()` rejects overflow lookups for `HFSPLUS_EXT_CNID` beyond first extents to avoid recursion. Free/truncate paths unlock the B-tree mutex while freeing allocation bitmap blocks, then relock with the same nested class. Error handling in truncate is limited and comments note missing propagation.
