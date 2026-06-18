# File Research: sources/os/bsd/netbsd-src/sys/sys/extattr.h

Read completely: 125 lines.

## Purpose
Defines the BSD extended-attribute namespace ABI, extattr control commands, kernel credential checks, and userland extattr functions.

## Main Interfaces
- Namespaces: `EXTATTR_NAMESPACE_EMPTY`, `USER`, `SYSTEM` and string names.
- `EXTATTR_NAMESPACE_NAMES` initializer.
- `EXTATTR_MAXNAMELEN`.
- Control commands: `EXTATTR_CMD_START`, `EXTATTR_CMD_STOP`.
- Kernel: `EXTATTR_LIST_LENPREFIX`, `extattr_check_cred`.
- Userland operations for fd/file/link: get, set, delete, list, control, namespace conversion, copy helpers, `fcpxattr`, `cpxattr`, `lcpxattr`.

## Dependencies And Integration
Ties user APIs to VFS extended attribute vnode operations and authorization via credentials.

## Risks And Edge Cases
- Namespace values and names are ABI-facing.
- List output can be length-prefixed via VOP flag.
- System namespace authorization depends on `extattr_check_cred`.

## Filesystem Relevance
High. Defines filesystem extended attribute user/kernel contract.
