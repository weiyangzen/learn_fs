# File Research: sources/os/linux/linux-stable/fs/udf/ialloc.c

## Summary
Implements UDF inode allocation and inode block freeing.

## Key Functions
- `udf_free_inode()`: frees the single block containing an inode’s file entry.
- `udf_new_inode()`: allocates and initializes a new VFS/UDF inode and reserves its file-entry block.

## Important Behavior
New inode format is selected from mount flags: extended file entry, short allocation descriptors, long allocation descriptors, or allocation descriptors in ICB. The code allocates the in-memory `i_data` buffer sized to the remaining block space after the chosen file entry header.

The inode block is allocated near the parent directory’s inode location and in the same partition. Ownership honors UDF mount UID/GID override flags, and the inode’s generation is derived from the logical volume unique ID.

`insert_inode_locked()` is used before returning the new inode, and the inode is marked dirty so the file entry is written.

## Risks
If allocation succeeds but inode insertion fails, the code marks the inode bad and drops it; freeing depends on eviction behavior. Format-selection flags determine how later extent and file data paths interpret `i_data`.
