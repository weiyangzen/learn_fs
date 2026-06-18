# File Research: sources/os/linux/linux-stable/fs/udf/directory.c

## Summary
Implements low-level UDF directory file-identifier iteration, validation, read-ahead, descriptor copying, descriptor rewriting, and directory block appending.

## Key Functions
- `udf_fiiter_init()`: initializes a directory iterator at a byte position and loads the current entry.
- `udf_fiiter_advance()`: advances to the next file identifier descriptor, crossing block and extent boundaries.
- `udf_fiiter_release()`: releases iterator buffers.
- `udf_fiiter_write_fi()`: writes an updated file identifier descriptor and recalculates its CRC/tag checksum.
- `udf_fiiter_update_elen()`: changes the current extent length and updates inode extent accounting.
- `udf_fiiter_append_blk()`: appends a new directory block at EOF.
- `udf_get_fileshortad()` / `udf_get_filelongad()`: parse short and long allocation descriptors from raw buffers.

## Important Behavior
`udf_verify_fi()` validates descriptor tag identity, implementation-use alignment, maximum entry size, entry bounds, and CRC length consistency. Entries larger than one filesystem block are rejected even though long implementation-use fields are theoretically allowed.

The iterator handles both inline directory data (`ICBTAG_FLAG_AD_IN_ICB`) and block-backed directories. For block-backed directories, it may hold two buffer heads when an entry or name crosses a block boundary.

Directory read-ahead is issued in 8 KiB windows at aligned positions inside a recorded allocated extent.

Write helpers can update descriptors spanning two buffers, recompute ITU-T CRC over descriptor payload, update tag checksum, dirty metadata buffers, and increment inode version.

## Risks
Variable-length directory entries can straddle block boundaries, so copy and CRC helpers must carefully split reads/writes between buffers. Directory mutation correctness depends on keeping file identifier CRCs, tag checksums, extent lengths, inode version, and metadata dirty tracking synchronized.
