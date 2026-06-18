# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_types.h

## Purpose

Defines basic UFS on-disk scalar types for DragonFly BSD.

## Definitions

- `ufs1_ino_t`: 32-bit unsigned inode number type for UFS1.
- `ufs_daddr_t`: 32-bit signed disk address type.
- `ufs_time_t`: 32-bit signed timestamp type.

## Dependencies And Integration Points

Included by UFS headers that need stable on-disk type widths. These typedefs complement broader kernel types such as `ino_t`, `daddr_t`, and filesystem-specific block address fields.

## Notes For Future Work

- The file is intentionally small and guarded by `_VFS_UFS_UFS_TYPES_H_`.
- Width choices matter for disk-format compatibility.
