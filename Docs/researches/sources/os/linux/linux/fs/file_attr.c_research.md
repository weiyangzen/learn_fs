# File Research: sources/os/linux/linux/fs/file_attr.c

Read status: complete, 486 lines.

Purpose: central VFS implementation for miscellaneous file attributes exposed through legacy ioctls and the `file_getattr` / `file_setattr` syscalls.

Key flow:
- `fileattr_fill_xflags()` and `fileattr_fill_flags()` translate between `FS_XFLAG_*` and legacy `FS_*_FL` flags.
- `vfs_fileattr_get()` checks LSM permission and calls filesystem `i_op->fileattr_get`.
- `vfs_fileattr_set()` checks ownership/capability, locks the inode, reads current attributes, fills unspecified fields from old attributes, validates policy in `fileattr_set_prepare()`, calls LSM set hook, invokes filesystem `fileattr_set`, and emits `fsnotify_xattr`.
- Legacy ioctl helpers wrap `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`, `FS_IOC_FSGETXATTR`, and `FS_IOC_FSSETXATTR`.
- `file_getattr` and `file_setattr` support pathname or `AT_EMPTY_PATH` fd targeting and copy extensible `struct file_attr` to/from userspace.

Important dependencies: inode operations, LSM hooks, fscrypt flag validation, idmapped mount ownership checks, mount write access, `copy_struct_*_user`.

Validation/security notes:
- Immutable and append-only flag changes require `CAP_LINUX_IMMUTABLE`.
- Project quota id changes are restricted to the initial user namespace.
- Extent-size, cowextsize, and DAX flags are type-restricted.
