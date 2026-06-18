# File Research: sources/os/linux/linux-stable/fs/debugfs/internal.h

## Purpose

Defines debugfs-private inode and file-removal bookkeeping structures shared by `inode.c` and `file.c`.

## Main Responsibilities

- Defines `struct debugfs_inode_info`, embedding the VFS inode plus a union of stored debugfs operation pointers.
- Provides `DEBUGFS_I()` to convert from `struct inode` to debugfs inode info.
- Declares debugfs proxy/noop file operation tables implemented in `file.c`.
- Defines `struct debugfs_fsdata`, the per-dentry active-user and cancellation state used during protected file access/removal.
- Defines method bit flags for llseek, read, write, poll, and ioctl availability.

## Important Dependencies

- VFS `struct inode`, `struct file_operations`, and debugfs public types.
- Refcount, completion, mutex, and list state used by removal coordination.

## Edge Cases and Risks

- `debugfs_inode_info` stores several mutually exclusive pointer types in a union; creators and proxy open paths must agree on which type was stored.
- `debugfs_fsdata` cancellation entries can point to stack-allocated objects, so removal and leave paths must serialize through `cancellations_mtx`.
