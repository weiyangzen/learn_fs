# sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/xattr.h

## Purpose
This header normalizes extended attribute APIs on FreeBSD to the Linux-style function names expected by common Ganesha code.

## Important APIs, Types, And Control Flow
It defines `XATTR_CREATE` and `XATTR_REPLACE` flag values and declares `fgetxattr`, `fsetxattr`, `flistxattr`, and `fremovexattr` wrappers operating on file descriptors. There is no control flow in the header; implementation lives in the FreeBSD OS support layer.

## State And Persistence
No in-memory state is defined. The underlying calls persist xattr changes on filesystem objects through `fsetxattr` and `fremovexattr`.

## Dependencies And Integration Points
It includes `<sys/errno.h>` and `<sys/types.h>` and is selected by `include/os/xattr.h` when building for FreeBSD. POSIX ACL conversion, NFSv4 ACL translation, and FSAL metadata paths can use these symbols through the OS abstraction.

## Risks And Test Signals
FreeBSD xattr namespaces and flag semantics do not perfectly match Linux. Tests should cover create-only, replace-only, list buffer sizing, removal of missing attributes, and ACL xattr round-trips on FreeBSD filesystems that support extended attributes.
