# File Research: sources/teaching/os161/kern/vfs/vfsfail.c

Provides typed stub implementations for vnode operations that are invalid or unsupported for a given vnode type. Because portable C does not allow safely sharing function pointers across incompatible signatures, each operation family has its own wrapper with matching arguments.

The stubs return specific errno values: `ENOTDIR` for directory-required operations on non-directories, `EISDIR` for file operations on directories, `EINVAL` for invalid operations, `ENOSYS` for unimplemented features, and `EPERM` for permission-denied mmap. Covered families include uio ops, mmap, truncate, creat, symlink, mkdir, link, remove/rmdir, rename, lookup, and lookparent.

Filesystems and device vnodes use these stubs to fill unsupported `vnode_ops` slots consistently.
