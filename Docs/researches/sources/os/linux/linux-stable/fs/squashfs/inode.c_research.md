# File Research: sources/os/linux/linux-stable/fs/squashfs/inode.c

## Summary
Reads Squashfs on-disk inodes from compressed metadata and initializes VFS inode objects for every supported inode type.

## Key APIs
- `squashfs_iget()`.
- `squashfs_read_inode()`.
- `squashfs_inode_ops`.

## Important Behavior
Squashfs inode identifiers encode a metadata block and offset. `squashfs_iget()` uses the on-disk inode number as the VFS inode cache key and fills new inodes via `squashfs_read_inode()`.

`squashfs_new_inode()` populates common mode, uid/gid, mtime/atime/ctime, inode number, and validates that the base mode does not already contain a file type.

The main switch handles regular and long regular files, directories and long directories, symlinks and long symlinks, devices, fifos, and sockets. It sets file operations, inode operations, address-space operations, sizes, nlinks, block counts, fragment metadata, block-list start, directory index metadata, parent inode, and special device numbers.

Extended inode forms can carry xattr ids. If xattrs are enabled and an xattr id table exists, `squashfs_xattr_lookup()` fills inode-private xattr location/count/size and charges xattr bytes to `i_blocks`.

## Risks
The parser relies on exact on-disk type-specific structure sizes and offsets. It validates fragment/file-size consistency and symlink size, but bad metadata can still fail reads deep in table lookups.
