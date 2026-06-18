# sources/sync-backup/rsync/lib/sysxattrs.h

## Purpose
`sysxattrs.h` declares rsync's portable extended attribute wrapper API and includes the platform headers needed by `sysxattrs.c` when xattr support is enabled.

## Important APIs, Types, and Functions
The header declares `sys_lgetxattr()`, `sys_fgetxattr()`, `sys_lsetxattr()`, `sys_lremovexattr()`, and `sys_llistxattr()`. It also normalizes `ENOATTR` to `ENODATA` on systems where Linux 2.4-style headers lack a distinct `ENOATTR` value.

## Control Flow
There is no runtime control flow. When `SUPPORT_XATTRS` is defined, the header includes one of `<sys/xattr.h>`, `<attr/xattr.h>`, or `<sys/extattr.h>` depending on configure results. When support is not enabled, it intentionally exposes no compatibility API.

## State and Persistence
The header owns no state and performs no persistence. It defines the call contract that implementation functions use to persist xattr changes through platform syscalls.

## Dependencies and Integration Points
The declarations are consumed by xattr transfer code and implemented by `sysxattrs.c`. The API deliberately resembles Linux xattr calls so higher-level rsync logic can use one call shape for path and descriptor xattr operations.

## Risks
The main risk is configuration drift: missing or incorrect `HAVE_*_XATTR_H` and platform xattr macros can leave the implementation without the expected prototypes or constants. The `ENOATTR` alias means callers should treat `ENOATTR` and `ENODATA` consistently but not assume platforms distinguish them.

## Test Signals
Header-level validation is mostly compile coverage across Linux, macOS, FreeBSD, and Solaris configurations. Integration tests should include builds with `SUPPORT_XATTRS` disabled to ensure callers are properly conditionalized.
