# File Research: sources/local-fs/btrfs-linux/fs/btrfs/export.h

## Summary
Defines the Btrfs exportfs file-handle structure and declares export-related entry points.

## Main Contents
- `extern const struct export_operations btrfs_export_ops`.
- Packed `struct btrfs_fid`.
- Declarations for `btrfs_get_dentry()` and `btrfs_get_parent()`.

## Important Details
`struct btrfs_fid` stores:
- inode objectid,
- inode root objectid,
- inode generation,
- parent objectid,
- parent generation,
- parent root objectid.

The parent root field is needed for cross-subvolume connectable file handles.

## Risks
The structure is packed and interpreted as a generic exportfs `u32` file-handle payload. Field size/order must stay compatible with `export.c` size macros and existing file-handle types.
