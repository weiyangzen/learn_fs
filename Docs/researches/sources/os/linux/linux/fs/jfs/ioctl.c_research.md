# File Research: sources/os/linux/linux/fs/jfs/ioctl.c

## Purpose
Implements JFS ioctl handling and VFS file-attribute get/set integration.

## Key Data
- `jfs_map[]` maps JFS inode flags to generic/ext2-style `FS_*` flags for noatime, dirsync, sync, secure deletion, undelete, append, and immutable.

## Key Functions
- `jfs_map_ext2()` translates flags between JFS internal and generic fileattr namespaces.
- `jfs_fileattr_get()` rejects special dentries, extracts user-visible flags from `JFS_IP(inode)->mode2`, translates them, and fills `struct file_kattr`.
- `jfs_fileattr_set()` rejects special dentries and fsx-style attrs, strips dirsync for non-directories, rejects quota files, preserves non-user-modifiable mode2 bits, applies file flags, updates ctime, and marks the inode dirty.
- `jfs_ioctl()` currently handles `FITRIM`: checks `CAP_SYS_ADMIN`, validates block-device discard support, copies `fstrim_range` from user space, raises `minlen` to discard granularity, calls `jfs_ioc_trim()`, copies the updated range back, and returns `-ENOTTY` for unknown commands.

## Dependencies
- Uses `jfs_dinode.h` for JFS flag definitions.
- Uses `jfs_discard.h` for `jfs_ioc_trim()`.
- Uses block-device discard helpers and Linux fileattr APIs.
