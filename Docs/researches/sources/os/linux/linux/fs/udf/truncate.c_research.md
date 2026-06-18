# File Research: sources/os/linux/linux/fs/udf/truncate.c

Purpose: UDF extent truncation and preallocation discard.

Key behavior:
- `extent_trunc()` rewrites an extent to a shorter length, converts unrecorded allocated extents to not-allocated when needed, and frees blocks beyond the new end.
- `udf_truncate_tail_extent()` trims the last extent to match `i_size`, warning if a full block or more exists past EOF.
- `udf_discard_prealloc()` removes a final preallocation extent and frees its blocks.
- `udf_update_alloc_ext_desc()` updates an indirect allocation extent descriptor length and descriptor tag.
- `udf_truncate_extents()` truncates all extents beyond `i_size`, handles indirect allocation descriptor blocks, frees now-unused indirect blocks, updates `i_lenAlloc` or allocation extent descriptors, and sets `i_lenExtents`.

Integration:
- Used by file size changes, symlink creation with external blocks, inode eviction/truncation paths, and extent allocation code.
- Depends on `udf_next_aext()`, `udf_current_aext()`, `udf_write_aext()`, `udf_delete_aext()`, `inode_bmap()`, and `udf_free_blocks()`.

Risks and invariants:
- AD-in-ICB files bypass external extent truncation.
- Extent modifications require correct allocation descriptor size for short vs long AD.
- On errors while walking extents, buffer heads are released and errors propagate.
