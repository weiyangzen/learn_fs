# File Research: sources/os/linux/linux-stable/fs/squashfs/squashfs_fs_i.h

## Summary
Defines Squashfs per-inode private state and the `squashfs_i()` container helper.

## Main Contents
- Shared fields: start block, metadata offset, xattr location/size/count, parent inode.
- Regular-file fields: fragment block/size/offset and block-list start.
- Directory fields: directory index start/offset/count.
- Embedded `struct inode vfs_inode`.

## Risks
The regular-file and directory-specific fields share a union. Callers must only interpret the union according to inode type initialized by `inode.c`.
