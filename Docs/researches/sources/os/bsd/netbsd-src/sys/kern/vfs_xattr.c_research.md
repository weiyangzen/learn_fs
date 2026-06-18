# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_xattr.c

Read completely: 1306 lines.

Implements NetBSD VFS extended attribute syscall glue. It exposes both the BSD `extattr_*` API and Linux-compatible `xattr` API, converting file descriptors or paths into vnodes and routing operations through vnode extended-attribute operations.

Core helpers:
- `extattr_check_cred()` delegates per-attribute access checks to kauth with `genfs_can_extattr()` as filesystem-independent policy input.
- `vfs_stdextattrctl()` is the default unsupported mount operation and unlocks the optional vnode before returning `EOPNOTSUPP`.
- `extattr_set_vp()`, `extattr_get_vp()`, `extattr_delete_vp()`, and `extattr_list_vp()` lock the target vnode, build `uio` structures when data buffers are present, call `VOP_*EXTATTR`, set syscall return values, and emit ktrace records.

BSD API coverage:
- `sys_extattrctl()` passes mount-level attribute-control commands to `VFS_EXTATTRCTL`, optionally resolving both a controlling path and an attribute backing file.
- Implements fd, file, and symlink-preserving variants for set, get, delete, and list.
- Path variants use `NSM_FOLLOW_NOEMULROOT` for file operations and `NSM_NOFOLLOW_NOEMULROOT` for link operations.
- List operations use `EXTATTR_LIST_LENPREFIX` for the BSD API.

Linux-compatible API:
- `sys_setxattr`, `sys_lsetxattr`, and `sys_fsetxattr` support `XATTR_CREATE`/`XATTR_REPLACE` checks by probing existing attributes before setting.
- `sys_getxattr`, `sys_lgetxattr`, and `sys_fgetxattr` support size-query semantics when the user data pointer is NULL.
- `sys_listxattr`, `sys_llistxattr`, and `sys_flistxattr` concatenate user namespace attributes and system namespace attributes; `EPERM` while listing system attributes is ignored.
- `sys_removexattr`, `sys_lremovexattr`, and `sys_fremovexattr` delete attributes.
- `xattr_native()` maps `system.`, `security.`, and `trusted.` names to `EXTATTR_NAMESPACE_SYSTEM`; `user.` and unrecognized names map to `EXTATTR_NAMESPACE_USER`.
- `XATTR_ERRNO()` maps `EOPNOTSUPP` to Linux-style `ENOTSUP`.

Risks and notes:
- All vnode helpers use exclusive vnode locking even for reads/lists.
- `extattr_delete_vp()` falls back to `VOP_SETEXTATTR(..., NULL, ...)` if `VOP_DELETEEXTATTR` is unsupported.
- Linux list operations can underflow the remaining `size` if a filesystem reports more user-list bytes than the provided size; this relies on VOP list behavior to respect `uio_resid`.
- Namespace mapping is intentionally coarse: Linux `security.` and `trusted.` attributes share NetBSD's system namespace.
