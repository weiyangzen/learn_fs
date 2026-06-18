# File Research: sources/os/linux/linux/fs/udf/ialloc.c

## Purpose
Implements UDF inode allocation and freeing.

## Main Functions
- `udf_free_inode()`: frees the inode’s file entry block through `udf_free_blocks()`.
- `udf_new_inode()`: allocates a new VFS inode and UDF file entry block, initializes UDF inode metadata, owner/mode, allocation descriptor type, timestamps, unique ID, and inserts the inode locked.

## Important Design Points
- Chooses Extended File Entry if mount flags request it and bumps UDF revision if needed.
- Allocates `i_data` sized to the remaining block after FE/EFE header.
- Allocates the file entry block near the parent directory’s location.
- Honors mount options for fixed UID/GID and allocation descriptor preference: in-ICB, short AD, or long AD.
- Initializes extra permissions and checkpoint state before marking inode dirty.

## Cross-File Relationships
- Uses block allocator from `balloc.c`.
- Uses permission helper `udf_update_extra_perms()` from `inode.c`.
- Inodes allocated here are later encoded by `udf_update_inode()` in `inode.c`.

## Risks / Review Notes
- If `insert_inode_locked()` fails after block allocation, the function returns error after `iput()` but the allocated block release depends on eviction/bad-inode behavior.
- The function returns `ERR_PTR()` on all failure paths and marks inodes bad before dropping references.
