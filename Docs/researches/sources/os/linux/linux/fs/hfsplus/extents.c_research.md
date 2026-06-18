# File Research: sources/os/linux/linux/fs/hfsplus/extents.c

Purpose: Implements HFS+ extent overflow handling, block mapping, fork freeing, file allocation growth, optional zeroout for B-tree nodes, and truncation.

Key functions:
- `hfsplus_ext_cmp_key()` compares extent keys by CNID, fork type, and start block.
- `hfsplus_ext_find_block()`, `hfsplus_ext_block_count()`, and `hfsplus_ext_lastblock()` interpret eight-entry HFS+ extent records.
- `hfsplus_ext_write_extent()` flushes dirty cached overflow extents under `extents_lock`.
- `hfsplus_get_block()` maps or allocates a file block, reading overflow extents as needed and marking dirty when cached extents are flushed.
- `hfsplus_free_fork()` frees inline and overflow extent records for a fork.
- `hfsplus_file_extend()` allocates allocation blocks, optionally zeroes them, appends to inline/cached extents, or creates a new overflow extent record.
- `hfsplus_file_truncate()` shrinks allocation, frees blocks, removes overflow records, and updates physical/fs block accounting.

Dependencies and integration:
- Uses allocation bitmap functions from `bitmap.c`.
- Called by inode/page-cache operations and by B-tree growth code.
- Marks allocation file and target inode dirty with HFS+ dirty-bit categories.

Risk notes:
- Extents tree file itself cannot be mapped through overflow extents in `hfsplus_get_block()`.
- Truncation deliberately unlocks the B-tree while freeing allocation bitmap blocks, then relocks with the correct subclass.
- Allocation-file size exhaustion returns ENOSPC rather than extending the allocation file dynamically.
