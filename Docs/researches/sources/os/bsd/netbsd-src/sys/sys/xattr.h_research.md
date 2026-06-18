# File Research: sources/os/bsd/netbsd-src/sys/sys/xattr.h

Read completely: 81 lines.

Defines Linux-compatible extended attribute user API declarations layered over NetBSD's extended attribute support, limited by comment to the user namespace for these calls.

Core definitions:
- `XATTR_NAME_MAX` maps to `KERNEL_NAME_MAX`, matching `EXTATTR_MAXNAMELEN` and Linux's 255-byte name maximum.
- `XATTR_SIZE_MAX` is 65536 but explicitly not enforced by NetBSD.
- `XATTR_CREATE` and `XATTR_REPLACE` select create-only or replace-only set semantics.

Userland API:
- Declares path, lpath, and fd variants for set, get, list, and remove: `setxattr`, `lsetxattr`, `fsetxattr`, `getxattr`, `lgetxattr`, `fgetxattr`, `listxattr`, `llistxattr`, `flistxattr`, `removexattr`, `lremovexattr`, and `fremovexattr`.

Risks and notes:
- The Linux-compatible size maximum is advisory in this header; actual filesystem/VFS behavior may differ.
- Declarations are hidden in `_KERNEL` builds.
