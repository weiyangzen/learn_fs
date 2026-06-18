# File Research: sources/os/linux/linux/fs/squashfs/export.c

Provides NFS/exportfs support.

SquashFS directory entries encode inode locations directly, but filehandles use inode numbers. This file maps inode numbers to on-disk inode locations via the compressed inode lookup table and its mount-time index table.

It implements filehandle-to-dentry, filehandle-to-parent, and get-parent operations, all using `squashfs_export_iget()`.

`squashfs_read_inode_lookup_table()` reads and validates the inode lookup index table, checking ordering and metadata-block distance constraints.
