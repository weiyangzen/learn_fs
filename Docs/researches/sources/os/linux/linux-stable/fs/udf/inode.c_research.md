# File Research: sources/os/linux/linux-stable/fs/udf/inode.c

## Summary
Core UDF inode implementation. It handles inode read/write, address-space operations, inline-file expansion, logical-to-physical block mapping, extent traversal/mutation, file size changes, indirect allocation extents, inode eviction, and descriptor serialization.

## Key Areas
- Address-space operations: `udf_read_folio()`, `udf_readahead()`, `udf_write_begin()`, `udf_write_end()`, `udf_writepages()`, `udf_direct_IO()`, and `udf_bmap()`.
- Block mapping: `udf_get_block()`, `udf_get_block_wb()`, `udf_map_block()`, `inode_getblk()`, and `inode_bmap()`.
- File growth/shrink: `udf_setsize()`, `udf_extend_file()`, `udf_do_extend_file()`, and `udf_do_extend_final_block()`.
- Extent editing: `udf_split_extents()`, `udf_prealloc_extents()`, `udf_merge_extents()`, `udf_update_extents()`, `udf_add_aext()`, `__udf_add_aext()`, `udf_write_aext()`, `udf_delete_aext()`, `udf_next_aext()`, and `udf_current_aext()`.
- Inode lifecycle: `udf_read_inode()`, `udf_update_inode()`, `udf_write_inode()`, `udf_evict_inode()`, `__udf_iget()`.
- Descriptor support: `udf_setup_indirect_aext()`, `udf_convert_permissions()`, `udf_update_extra_perms()`.

## Important Behavior
UDF supports files stored directly inside the file entry (`AD_IN_ICB`) and extent-backed files using short or long allocation descriptors. Inline files have special read/write/writeback paths and are expanded to normal extent-backed files when they no longer fit.

Extent mapping distinguishes recorded allocated extents, not-recorded allocated preallocation extents, not-recorded not-allocated holes, and next-allocation-descriptor extents. When allocating a block, the code may split a hole/preallocated extent into before/current/after extents, add preallocation, merge adjacent extents, and write the modified descriptor list back.

The extent cache stores a recently used allocation descriptor position under `i_extent_cache_lock`; mutations clear it under `i_data_sem`.

`udf_read_inode()` reads FE/EFE/USE descriptors, follows strategy-4096 indirect ICBs with a hard nesting limit, validates allocation descriptor lengths, sets VFS operations according to UDF file type, and initializes special devices from extended attributes.

`udf_update_inode()` serializes in-memory inode state back to FE/EFE/USE descriptors, including permissions, link count, size, timestamps, unique ID, allocation descriptor lengths, device extended attributes, descriptor CRC, and tag checksum.

## Synchronization
- `i_data_sem` protects allocation descriptor data and inline data transitions.
- `i_extent_cache_lock` protects cached extent positions.
- Page-cache invalidate locking is used around inline-file expansion and file-size writes.
- Metadata buffer dirtying uses UDF’s metadata buffer tracking so fsync can flush related descriptor blocks.

## Risks
This file edits complex variable-length extent lists, sometimes spanning indirect allocation extent blocks. Failure during insertion/update can leak blocks or leave extent metadata inconsistent; the code explicitly comments that insertion failure may corrupt the extent list and tries to stop early. Inline-to-extent conversion also has careful rollback to avoid data loss if writeback fails.
