# File Research: sources/os/linux/linux/fs/squashfs/inode.c

Decodes on-disk SquashFS inodes into VFS inodes.

`squashfs_new_inode()` fills common uid/gid, mode, mtime/ctime/atime, and validates that the base mode does not already contain a file type. `squashfs_iget()` wraps `iget_locked()` and calls `squashfs_read_inode()` for new inodes.

`squashfs_read_inode()` handles regular, long regular, directory, long directory, symlink, device, FIFO, and socket inode formats. It wires file ops, inode ops, address-space ops, fragment metadata, directory indexes, parent inode numbers, nlink, blocks, and xattr metadata.

It validates corrupt states such as zero inode numbers, impossible fragments, negative long sizes, oversized symlinks, unknown inode types, and xattr lookup failures.
