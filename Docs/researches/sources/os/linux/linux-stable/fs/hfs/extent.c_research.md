# File Research: sources/os/linux/linux-stable/fs/hfs/extent.c

## Scope

Manages classic HFS extent records, overflow extent cache writeback/read, block mapping, file extension, fork freeing, and truncation.

## APIs And Behavior

- `hfs_ext_keycmp()` orders extents by CNID, fork type, then allocation block number.
- `hfs_ext_find_block()` maps a fork-relative allocation-block offset through a three-entry extent record.
- `hfs_ext_write_extent()` writes dirty cached overflow extents, inserting new overflow records or overwriting existing ones.
- `hfs_get_block()` maps VFS logical blocks to physical disk sectors and allocates blocks for extending writes.
- `hfs_extend_file()` finds free allocation blocks, appends them to first extents or cached overflow extents, or creates a new overflow record when the current extent record is full.
- `hfs_free_fork()` frees first and overflow extents for a data/resource fork and removes overflow records.
- `hfs_file_truncate()` grows sparse page-cache state when `i_size` exceeds physical size, or frees extents and overflow records when shrinking.

## State And Dependencies

Per-inode extent state includes first extents, cached overflow extents, first/cached block counts, allocation block count, physical size, filesystem block count, and dirty/new extent flags. The file depends on the volume bitmap, extents B-tree, block mapper, page-cache write helpers, MDB dirtying, and allocation block geometry from `HFS_SB`.

## Risks And Invariants

The cached overflow record must be flushed before replacing it. Allocation and truncation require `extents_lock` to serialize cached extent state. Shrink paths free blocks while removing overflow records, but error handling is limited and comments note missing propagation for `hfs_file_truncate()`.
