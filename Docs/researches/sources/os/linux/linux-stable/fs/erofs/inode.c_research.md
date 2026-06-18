# File Research: sources/os/linux/linux-stable/fs/erofs/inode.c

## Summary
Loads EROFS inodes, assigns operations, handles symlinks, getattr/statx, ioctl, and inode lookup by NID.

## Main Responsibilities
- Reads compact or extended on-disk inode records.
- Decodes mode, uid/gid, nlink, size, timestamps, block/chunk/compression metadata.
- Initializes regular, directory, symlink, and special inode operations.
- Supports fast inline symlinks.
- Reports immutable/compressed statx attributes and DIO alignment.
- Implements `FS_IOC_GETFSLABEL`.

## Key APIs
- `erofs_iget()`
- `erofs_getattr()`
- `erofs_ioctl()`
- `erofs_generic_iops`

## Important Behavior
`iget5_locked()` keys the inode cache by NID while squashing inode numbers for 32-bit `ino_t`. Compressed inodes require zip support and available algorithms. DAX is enabled only for eligible flat/chunk regular files.

## Risks
On-disk inode parsing validates unsupported layouts, negative sizes, invalid chunk formats, and bogus modes. Metabox and 48-bit addressing affect inode location and inode-number presentation.
