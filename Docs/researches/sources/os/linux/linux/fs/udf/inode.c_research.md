# File Research: sources/os/linux/linux/fs/udf/inode.c

## Purpose
Core UDF inode implementation: page-cache address-space operations, in-ICB small-file handling, logical-to-physical block mapping, extent allocation/mutation, truncation/extension, inode read/write encoding, allocation descriptor traversal, and extent cache management.

## Main Areas
- Extent cache:
  - `udf_clear_extent_cache()`, `udf_read_extent_cache()`, `udf_update_extent_cache()`.
- VFS/page-cache operations:
  - `udf_evict_inode()`
  - `udf_write_failed()`
  - `udf_writepages()`
  - `udf_read_folio()`
  - `udf_readahead()`
  - `udf_write_begin()` / `udf_write_end()`
  - `udf_direct_IO()`
  - `udf_bmap()`
  - `udf_aops`
- In-ICB conversion:
  - `udf_expand_file_adinicb()`
- Block mapping/allocation:
  - `udf_map_block()`
  - `udf_get_block()`
  - `inode_getblk()`
  - `udf_bread()`
- Extent extension and mutation:
  - `udf_do_extend_file()`
  - `udf_do_extend_final_block()`
  - `udf_extend_file()`
  - `udf_split_extents()`
  - `udf_prealloc_extents()`
  - `udf_merge_extents()`
  - `udf_update_extents()`
- Size and inode lifecycle:
  - `udf_setsize()`
  - `udf_read_inode()`
  - `udf_update_inode()`
  - `__udf_iget()`
  - `udf_write_inode()`
- Allocation descriptor helpers:
  - `udf_setup_indirect_aext()`
  - `__udf_add_aext()`
  - `udf_add_aext()`
  - `udf_write_aext()`
  - `udf_next_aext()`
  - `udf_current_aext()`
  - `udf_insert_aext()`
  - `udf_delete_aext()`
  - `inode_bmap()`

## Important Design Points
- UDF supports three data allocation modes: short allocation descriptors, long allocation descriptors, and data embedded directly in the ICB/file entry.
- In-ICB files use custom read/write behavior and fall back to buffered I/O for direct I/O.
- Writeback must not allocate blocks; allocation happens on write/page fault paths.
- Extent mutation works by reading neighboring extents into a small array, splitting, optionally preallocating, merging, then writing/inserting/deleting descriptors.
- Indirect allocation extents are supported, with a hard cap on indirect extent chaining (`UDF_MAX_INDIR_EXTS`).
- ICB strategy 4096 indirection is supported during inode read, capped by `UDF_MAX_ICB_NESTING`.
- `udf_update_inode()` rewrites FE/EFE/USE blocks from in-memory inode state, recomputing CRC and tag checksum.

## Corruption / Validation Guards
- Partition reference and logical block bounds checked before inode read.
- Descriptor tag must be FE, EFE, or USE.
- Unsupported ICB strategy and allocation descriptor types are rejected.
- Allocation descriptor and extended attribute lengths are checked against block size and allocation offsets.
- In-ICB file size must match `i_lenAlloc` and fit inside the file entry.
- Excessive ICB hierarchy and indirect extent nesting are rejected.

## Cross-File Relationships
- Uses media structs/constants from `ecma_167.h`.
- Uses block allocation from `balloc.c`.
- Used by `file.c`, `dir.c`, `directory.c`, `ialloc.c`, symlink/truncate/namei code outside this group.
- Supplies `udf_get_block()` to VFS buffer/page-cache helpers.
- Supplies allocation descriptor APIs consumed by `balloc.c` and `directory.c`.

## Risks / Review Notes
- Extent mutation is the highest-risk logic: split/prealloc/merge/update must preserve block accounting, free preallocated blocks correctly, and keep descriptor lists consistent.
- `udf_update_extents()` comments acknowledge possible corruption/leaks if insertion fails mid-update.
- `udf_current_aext()` returns `-1` for some malformed allocation descriptor bounds, not a specific errno.
- In-ICB conversion has rollback logic if data writeback fails, but depends on folio contents and inode data remaining coherent.
