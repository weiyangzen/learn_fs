# File Research: sources/os/linux/linux-stable/fs/proc/fd.h

## Purpose

Declares proc fd/fdinfo operations and a helper to retrieve the fd number stored in a proc inode.

## Main Contents

- Extern declarations:
  - `proc_fd_operations`
  - `proc_fd_inode_operations`
  - `proc_fdinfo_operations`
  - `proc_fdinfo_inode_operations`
  - `proc_fd_permission()`
- Inline helper:
  - `proc_fd(struct inode *inode)` returns `PROC_I(inode)->fd`.

## Notes

This header is used by proc base code and `fd.c` to share fd directory operations.
