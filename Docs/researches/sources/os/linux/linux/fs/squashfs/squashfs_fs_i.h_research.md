# File Research: sources/os/linux/linux/fs/squashfs/squashfs_fs_i.h

Defines the in-memory SquashFS inode extension.

`struct squashfs_inode_info` stores common on-disk location fields, xattr metadata, parent inode number, and a union of regular-file fragment/block-list state or directory-index state, followed by the embedded VFS inode.

`squashfs_i()` converts a VFS inode pointer to the SquashFS inode wrapper via `container_of()`.
