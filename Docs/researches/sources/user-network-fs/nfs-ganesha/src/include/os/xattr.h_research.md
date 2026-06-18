# sources/user-network-fs/nfs-ganesha/src/include/os/xattr.h

## Purpose
This wrapper selects the platform extended-attribute API for common Ganesha code.

## Important APIs, Types, And Control Flow
It includes Linux `<sys/xattr.h>` when `LINUX` is set and FreeBSD `<os/freebsd/xattr.h>` when `FREEBSD` is set. It has no functions of its own.

## State And Persistence
No wrapper state exists. Underlying xattr calls persist metadata on filesystem objects.

## Dependencies And Integration Points
The wrapper is used by POSIX ACL xattr conversion, FSAL metadata operations, and any NFS attribute path that needs extended attributes without platform-specific includes.

## Risks And Test Signals
Linux and FreeBSD xattr namespace behavior differs. Test signals include ACL xattr serialization, user/system/security namespace access, create/replace flags, and builds on both platforms.
