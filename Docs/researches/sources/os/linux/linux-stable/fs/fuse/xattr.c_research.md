# File Research: sources/os/linux/linux-stable/fs/fuse/xattr.c

## Purpose
Implements FUSE extended attribute operations and installs a generic xattr handler.

## Key Interfaces
- `fuse_setxattr()`, `fuse_getxattr()`, `fuse_listxattr()`, and `fuse_removexattr()` send FUSE xattr protocol requests.
- `fuse_xattr_get()` and `fuse_xattr_set()` adapt VFS xattr handler calls.
- `fuse_xattr_handlers[]` exports the handler table.

## Control Flow And Behavior
Each operation checks per-connection `no_*xattr` feature-disable bits. `GETXATTR` and `LISTXATTR` use a size-query mode when the user buffer size is zero and clamp returned sizes to Linux maxima. `LISTXATTR` validates returned lists as NUL-terminated nonempty names. `SETXATTR` can use the extended setxattr input size when negotiated.

## Dependencies
Uses FUSE simple requests, Linux xattr and POSIX ACL xattr constants, inode bad-state checks, process permission checks, and ctime updates.

## Risks And Invariants
`-ENOSYS` permanently disables the corresponding operation on the connection and returns `-EOPNOTSUPP`. Successful set/remove updates ctime. Returned xattr lists are treated as protocol data and verified.
