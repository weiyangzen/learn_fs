# File Research: sources/os/linux/linux-stable/fs/udf/truncate.c

## Summary
Implements UDF extent truncation, tail-extent cleanup, preallocation discard, allocation extent descriptor updates, and block freeing when files shrink.

## Main Responsibilities
- Truncates the final extent to match `i_size`.
- Frees recorded or allocated-not-recorded blocks beyond EOF.
- Deletes trailing preallocation extents.
- Updates allocation extent descriptors and descriptor tags after shrinking allocation lists.
- Frees indirect allocation extent blocks when their contents are removed.

## Important Behavior
`extent_trunc()` converts allocated-not-recorded extents to unallocated when partially preserved and frees the discarded block range according to extent type.

`udf_truncate_extents()` uses `inode_bmap()` to find the extent containing the new EOF, truncates that extent, then walks following extents and indirect allocation descriptors to delete or free them.

## Risks
This code assumes the caller is shrinking the file; extension is handled elsewhere. Correct `epos.offset` adjustment by short vs long allocation descriptor size is critical when rewriting the current extent.
