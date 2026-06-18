# File Research: sources/os/linux/linux/fs/udf/balloc.c

## Purpose
Implements UDF block allocation and freeing for partitions backed either by unallocated-space bitmaps or unallocated-space tables.

## Main Functions
- Bitmap path:
  - `read_block_bitmap()`: reads and verifies bitmap blocks, checking reserved/invalid free bits.
  - `load_block_bitmap()`: lazy-loads bitmap group buffers and preserves prior verification errors.
  - `udf_bitmap_free_blocks()`: sets free bits and updates free-space counters.
  - `udf_bitmap_prealloc_blocks()`: consumes consecutive free bits from a target block.
  - `udf_bitmap_new_block()`: finds and clears a free bit near the goal block.
- Table path:
  - `udf_table_free_blocks()`: merges freed ranges into unallocated-space extent table, including indirect extent setup when needed.
  - `udf_table_prealloc_blocks()`: consumes blocks from an exact free-table extent.
  - `udf_table_new_block()`: selects the closest free extent to the goal and allocates from its beginning.
- Public wrappers:
  - `udf_free_blocks()`
  - `udf_prealloc_blocks()`
  - `udf_new_block()`

## Important Design Points
- Allocation is serialized by `s_alloc_mutex`.
- Logical Volume Integrity Descriptor free-space table is updated through `udf_add_free_space()` when available.
- Bitmap semantics use set bit = free and clear bit = allocated.
- Frees validate overflow and partition length before modifying allocation metadata.
- Table allocation avoids splitting extents by allocating from the beginning of the chosen extent.

## Cross-File Relationships
- Used by `ialloc.c` for inode block allocation/freeing.
- Used heavily by `inode.c` for data block allocation, preallocation, extent splitting/merging, and indirect allocation extents.
- Relies on extent helper APIs from `inode.c`/UDF headers, e.g. `udf_next_aext`, `udf_write_aext`, `udf_setup_indirect_aext`, `__udf_add_aext`.

## Risks / Review Notes
- Some table-free error paths jump to cleanup but do not surface errors to public callers because `udf_free_blocks()` is void.
- `udf_bitmap_new_block()` maps any bitmap load error to `-EIO`, even if the verification failure was `-EFSCORRUPTED`.
- The table-free path can “steal” a block from the extent being freed to create an indirect allocation extent; this is subtle and depends on count/length adjustments staying correct.
