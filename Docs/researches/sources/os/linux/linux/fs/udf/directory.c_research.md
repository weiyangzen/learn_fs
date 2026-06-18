# File Research: sources/os/linux/linux/fs/udf/directory.c

## Purpose
Provides low-level UDF directory File Identifier Descriptor iteration and update helpers.

## Main Functions
- `udf_verify_fi()`: validates FID tag identity, impUse alignment, entry size, EOF bounds, and CRC length.
- `udf_copy_fi()`: copies a FID and name from in-ICB data or one/two buffer_heads, handling entries that cross block boundaries.
- `udf_readahead_dir()`, `udf_fiiter_bread_blk()`: block readahead and read helpers.
- `udf_fiiter_advance_blk()`: advances to the next directory block/extent and verifies allocation type.
- `udf_fiiter_load_bhs()`: ensures the current and optional next block are loaded.
- `udf_fiiter_init()`, `udf_fiiter_advance()`, `udf_fiiter_release()`: iterator lifecycle.
- `udf_fiiter_write_fi()`: writes back modified FID with recalculated CRC/checksum.
- `udf_fiiter_update_elen()`: updates the current directory extent length.
- `udf_fiiter_append_blk()`: appends a new directory block at EOF.
- `udf_get_fileshortad()`, `udf_get_filelongad()`: parse short/long allocation descriptors from raw data.

## Important Design Points
- Supports directories stored in ICB and directories stored in allocated extents.
- Directory entries can straddle block boundaries; the iterator tracks up to two buffer_heads and uses `namebuf` when names cross.
- FID writeback updates both descriptor CRC and tag checksum.
- Directory mutation increments inode version, which coordinates with `dir.c` readdir position validation.

## Cross-File Relationships
- Used by `dir.c` for readdir.
- Used by name lookup/update code outside this group.
- Uses allocation descriptor helpers consumed by `inode.c`.

## Risks / Review Notes
- `namebuf` allocation uses `GFP_KERNEL | __GFP_NOFAIL` because later directory-update paths may be hard to unwind safely.
- Unsupported huge `lengthOfImpUse` entries are treated as corruption even though the spec may allow them.
- Several corruption checks return `-EFSCORRUPTED`, making this file a key media validation point.
