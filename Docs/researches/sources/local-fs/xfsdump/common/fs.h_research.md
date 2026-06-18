# File Research: sources/local-fs/xfsdump/common/fs.h

## Summary
Declares filesystem utility interfaces used to identify dump sources and query basic XFS filesystem properties.

## Main Contents
- Default name/path limits: `FS_MAXNAMELEN_DEFAULT` and `FS_MAXPATHLEN_DEFAULT`.
- `fs_info()` for resolving source name to type, device, mount point, and UUID.
- `fs_mounted()` for checking mounted status.
- `fs_getid()` for retrieving filesystem UUID.
- `fs_getinocnt()` for counting in-use inodes.

## Risks
The header describes generic filesystem utilities, but the implementation’s UUID lookup is XFS ioctl based.

Callers must provide correctly sized writable buffers for `fs_info()` outputs.
