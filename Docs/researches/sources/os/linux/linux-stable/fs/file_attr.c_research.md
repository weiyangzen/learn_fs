# File Research: sources/os/linux/linux-stable/fs/file_attr.c

This file implements the generic VFS layer for miscellaneous file attributes, bridging legacy ioctl interfaces, the newer `file_getattr`/`file_setattr` syscalls, LSM hooks, and filesystem `fileattr_get`/`fileattr_set` inode operations.

Major responsibilities:
- Translate between legacy `FS_*_FL` flags and `FS_XFLAG_*` xflags.
- Retrieve file attributes through `vfs_fileattr_get()`, including security checks.
- Validate and apply attribute changes through `vfs_fileattr_set()`.
- Marshal `fsxattr` and `file_attr` structures to and from userspace.
- Implement ioctl helpers for `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`, `FS_IOC_FSGETXATTR`, and `FS_IOC_FSSETXATTR`.
- Implement `file_getattr` and `file_setattr` syscalls with path lookup, `AT_EMPTY_PATH`, and structure-size extensibility.

Important design points:
- `fileattr_set_prepare()` centralizes generic validity checks before filesystem-specific mutation.
- Attribute setting first reads current attributes so unspecified fields can inherit existing state.
- Immutable and append-only changes require `CAP_LINUX_IMMUTABLE`.
- Project ID changes are restricted to the initial user namespace and validated as kernel project IDs.
- Extent-size, COW extent-size, inherited extent-size, and DAX xflags are constrained by file type.
- Legacy ioctl and syscall paths both converge on `vfs_fileattr_set()` and mount write accounting.

Key invariants:
- Filesystems without `fileattr_get` or `fileattr_set` return `-ENOIOCTLCMD`, translated to `-EOPNOTSUPP` for the new syscalls.
- Read-only xflags are masked out when converting user-settable attributes.
- The inode lock is held across current-attribute retrieval, validation, security checks, filesystem mutation, and notification.
- `file_setattr` and ioctl setters must acquire mount write access before mutation.
- Zero extent-size hints clear their corresponding xflag bits.

External interfaces:
- Exports `fileattr_fill_xflags`, `fileattr_fill_flags`, `vfs_fileattr_get`, `vfs_fileattr_set`, and `copy_fsxattr_to_user`.
- Defines syscall entry points `file_getattr` and `file_setattr`.
