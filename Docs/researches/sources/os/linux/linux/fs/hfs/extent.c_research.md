# File Research: sources/os/linux/linux/fs/hfs/extent.c

Purpose: Implements classic HFS extent overflow management, file block mapping, allocation, fork freeing, file extension, and truncation.

Key functions:
- `hfs_ext_keycmp()` sorts extent keys by file CNID, fork type, and allocation block number.
- `hfs_ext_find_block()` maps an allocation-block offset through a three-entry extent record.
- `hfs_ext_write_extent()` flushes dirty cached overflow extents into the extents B-tree.
- `hfs_free_fork()` frees inline and overflow extents for a file fork.
- `hfs_get_block()` maps or allocates logical file blocks for buffer/page-cache I/O.
- `hfs_extend_file()` allocates new allocation blocks, appends to inline/cached extents, or starts a new overflow extent record.
- `hfs_file_truncate()` frees excess allocation blocks and removes overflow extent records as needed.

Dependencies and integration:
- Uses volume bitmap APIs `hfs_vbm_search_free()` and `hfs_clear_vbm_bits()`.
- Uses B-tree search/mutation for overflow extents and marks MDB/alternate MDB dirty when allocation changes.
- Called by address-space operations in `inode.c`.

Risk notes:
- Uses 16-bit allocation block counts, matching classic HFS limits.
- Truncate error handling is explicitly incomplete in comments.
- Extent cache state flags must be kept consistent or dirty extents can be lost or duplicated.
