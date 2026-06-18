# File Research: sources/os/linux/linux-stable/fs/erofs/internal.h

## Summary
Defines EROFS in-kernel private structures, flags, helpers, and cross-module interfaces.

## Main Contents
- `struct erofs_sb_info`
- `struct erofs_inode`
- Device, fscache, domain, xattr-prefix, buffer, map, and map-device structures.
- Mount option flags.
- Feature-check helper macros.
- Metadata, mapping, inode, file, fscache, fileio, compression, sysfs, shrinker, and inode-share declarations.

## Important Details
The header centralizes mode selection: compressed inodes use `z_erofs_aops`, fscache mode uses `erofs_fscache_access_aops`, file-backed mode uses `erofs_fileio_aops`, otherwise normal `erofs_aops`.

## Risks
Many compile-time feature stubs are defined here. Callers must handle `-EOPNOTSUPP` when a feature-dependent implementation is absent.
