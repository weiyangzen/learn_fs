# File Research: sources/os/linux/linux/fs/debugfs/internal.h

## Role

Internal debugfs declarations shared between `inode.c` and `file.c`.

## Main Types

`struct debugfs_inode_info` wraps a VFS inode and stores one of:

- Raw pointer.
- Real `file_operations`.
- Short debugfs fops.
- Automount callback.

It also stores an auxiliary pointer.

`DEBUGFS_I()` converts a VFS inode to the debugfs inode wrapper.

`struct debugfs_fsdata` stores per-dentry file operation safety state:

- Full or short fops pointers.
- Active-user refcount and drained completion.
- Cancellation mutex and list.
- Method bitmask.

## Operation Flags

Defines method bits used by proxy fops:

- `HAS_READ`
- `HAS_WRITE`
- `HAS_LSEEK`
- `HAS_POLL`
- `HAS_IOCTL`

## Shared Declarations

Declares debugfs proxy operation tables implemented in `file.c`:

- `debugfs_noop_file_operations`
- `debugfs_open_proxy_file_operations`
- `debugfs_full_proxy_file_operations`
- `debugfs_full_short_proxy_file_operations`

## Research Notes

This header is the contract between debugfs inode lifecycle and file operation proxying. Its key structure, `debugfs_fsdata`, is allocated lazily by file access and freed by dentry release.
