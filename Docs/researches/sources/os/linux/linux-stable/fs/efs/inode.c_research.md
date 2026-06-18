# File Research: sources/os/linux/linux-stable/fs/efs/inode.c

## Summary
Implements EFS inode loading, address-space operations, extent decoding, and logical-to-physical block mapping.

## Main Responsibilities
- Reads on-disk inodes from cylinder group layout.
- Converts extent byte fields into CPU-order extent records.
- Initializes VFS inode mode, ownership, times, size, device IDs, and file operations.
- Maps logical blocks through direct or indirect extents.

## Key APIs
- `efs_iget()`
- `efs_map_block()`

## Important Behavior
Inode block and offset are computed from EFS cylinder group metadata. Regular files use `generic_ro_fops` and block read aops. Symlinks use a custom symlink address-space op. Extent mapping caches the last successful extent in `lastextent`.

## Risks
Indirect extent search is subtle and depends on old EFS extent layout. Corrupt extent magic or unsupported inode modes fail inode loading.
