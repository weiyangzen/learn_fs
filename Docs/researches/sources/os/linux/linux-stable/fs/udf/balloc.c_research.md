# File Research: sources/os/linux/linux-stable/fs/udf/balloc.c

## Summary
Implements UDF block allocation and free-space management for both bitmap-backed and table-backed unallocated-space representations.

## Key Functions
- `udf_free_blocks()`: public free path; validates block ranges, dispatches to bitmap or table freeing, and updates inode block accounting.
- `udf_prealloc_blocks()`: public preallocation path; allocates a contiguous run from bitmap/table metadata and updates inode block accounting.
- `udf_new_block()`: public single-block allocation path; dispatches to bitmap/table allocator and updates inode block accounting.
- `udf_bitmap_new_block()`, `udf_bitmap_prealloc_blocks()`, `udf_bitmap_free_blocks()`: bitmap allocator implementation.
- `udf_table_new_block()`, `udf_table_prealloc_blocks()`, `udf_table_free_blocks()`: unallocated-space table allocator implementation.
- `read_block_bitmap()` / `load_block_bitmap()`: lazy-load and verify bitmap blocks.
- `udf_add_free_space()`: updates the logical volume integrity descriptor free-space table.

## Important Behavior
Bitmap allocation treats set bits as free. Allocation clears bits, freeing sets bits, and bitmap block zero/one consistency is checked when blocks are first loaded.

Table allocation manipulates extents in the unallocated-space table. It can merge newly freed ranges with adjacent free extents, allocate from the nearest free extent to a goal block, and split or delete extents as space is consumed.

All allocator mutations are serialized by `s_alloc_mutex`. Free-space accounting is reflected into the LVID when available and marks it updated.

## Risks
The table allocator edits allocation descriptors while holding the allocator mutex and has special logic to avoid recursively allocating metadata while freeing blocks. Corruption handling is defensive but not always recoverable: bitmap verification failures are cached as error pointers, and table extent insertion failures can leave allocation metadata damaged.
