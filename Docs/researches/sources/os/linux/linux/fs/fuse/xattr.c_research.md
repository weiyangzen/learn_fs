# File Research: sources/os/linux/linux/fs/fuse/xattr.c

Implements FUSE extended attribute operations and registers the VFS xattr handler.

Key entry points:
- `fuse_setxattr()`
- `fuse_getxattr()`
- `fuse_listxattr()`
- `fuse_removexattr()`
- `fuse_xattr_handlers[]`

Important control flow:
- Set/get/list/remove each sends the corresponding FUSE opcode and marks the connection operation unsupported after `-ENOSYS`, translating to `-EOPNOTSUPP`.
- `fuse_setxattr()` uses extended setxattr input size only when `fc->setxattr_ext` is enabled.
- `fuse_getxattr()` and `fuse_listxattr()` use the common “size query when size is zero, data transfer when size is nonzero” pattern.
- `fuse_verify_xattr_list()` validates returned xattr list entries are nonempty NUL-terminated strings.

Dependencies and integration:
- Uses FUSE protocol args plus Linux xattr and POSIX ACL xattr headers.
- VFS handler has empty prefix, allowing all namespaces to be forwarded to userspace.

Risks and invariants:
- Bad inodes return `-EIO`; list also enforces `fuse_allow_current_process()`.
- Size query results are capped to `XATTR_SIZE_MAX` or `XATTR_LIST_MAX`.
- Successful set/remove updates ctime.
