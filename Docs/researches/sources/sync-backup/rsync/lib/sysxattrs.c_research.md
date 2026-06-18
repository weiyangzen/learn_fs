# sources/sync-backup/rsync/lib/sysxattrs.c

## Purpose
`sysxattrs.c` provides rsync's portable extended-attribute syscall wrapper layer. It exposes a Linux-like lget/fget/lset/lremove/llist API while hiding platform differences among Linux, macOS, FreeBSD, and Solaris xattr implementations.

## Important APIs, Types, and Functions
The exported functions are `sys_lgetxattr()`, `sys_fgetxattr()`, `sys_lsetxattr()`, `sys_lremovexattr()`, and `sys_llistxattr()`. Solaris also has the internal helper `read_xattr()` for reading file-backed attributes from a descriptor. macOS defines `GETXATTR_FETCH_LIMIT` to handle resource forks larger than the platform's single-call fetch limit.

## Control Flow
Under `SUPPORT_XATTRS`, preprocessor branches select a platform. Linux is a direct wrapper around `lgetxattr()`, `fgetxattr()`, `lsetxattr()`, `lremovexattr()`, and `llistxattr()`. macOS adds `XATTR_NOFOLLOW` for path operations and loops additional `getxattr()` calls with offsets when a fetch returns exactly 64 MiB but the requested size is larger. FreeBSD wraps `extattr_*` in the user namespace and converts the list format from length-prefixed strings into NUL-terminated strings in place. Solaris treats xattrs as files in an attribute directory, using `attropen()`, `openat(... O_XATTR)`, reads and writes, `unlinkat()`, and directory iteration.

## State and Persistence
The functions do not maintain process state. `sys_lsetxattr()` and `sys_lremovexattr()` persist changes to filesystem xattrs. Solaris operations open temporary descriptors and close them in all normal paths; list operations create a `DIR *` from the xattr directory descriptor.

## Dependencies and Integration Points
The file depends on `rsync.h`, `sysxattrs.h`, platform xattr headers, descriptor I/O, directory traversal, and errno normalization. It is used by rsync's higher-level xattr preservation code, which expects Linux-style size-probe, fetch, list, set, and remove behavior even on non-Linux systems.

## Risks
FreeBSD list conversion is sensitive to malformed kernel output and signals `EINVAL` when lengths overrun. Solaris `sys_lsetxattr()` writes chunks using `size` rather than `size - bufpos`, which deserves scrutiny for partial-write behavior. The macOS 64 MiB loop depends on offset types and only engages when the initial fetch exactly hits the limit. Namespace mismatches can hide non-user attributes on FreeBSD.

## Test Signals
Useful tests include size-probe calls with `value == NULL`, symlink xattrs, values larger than macOS's chunk limit, FreeBSD list conversion with multiple attributes, Solaris attribute read/write/remove, ERANGE retry behavior, and preservation round trips through rsync's `-X` option.
