# File Research: sources/os/linux/linux-stable/fs/efs/super.c

## Summary
Implements EFS filesystem registration, mount, superblock validation, SGI volume header handling, statfs, and inode-cache setup.

## Main Responsibilities
- Registers the `efs` filesystem.
- Allocates/free EFS inode cache objects.
- Parses SGI volume headers and finds EFS slices.
- Validates EFS superblocks.
- Forces read-only mounts.
- Provides NFS export operations.

## Key APIs
- `efs_fill_super()`
- `efs_validate_vh()`
- `efs_validate_super()`

## Important Behavior
Mount reads block 0 as an SGI volume header, optionally derives an EFS partition start, then reads the EFS superblock. The root inode is loaded from `EFS_ROOTINODE`. Reconfigure always sets `SB_RDONLY`.

## Risks
Several early mount error paths return without freeing `s_fs_info` directly, relying on mount teardown. On-disk volume headers and superblocks are minimally validated for old-media compatibility.
