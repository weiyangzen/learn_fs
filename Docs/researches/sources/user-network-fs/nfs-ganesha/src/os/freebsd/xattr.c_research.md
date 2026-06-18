<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/xattr.c -->
# sources/user-network-fs/nfs-ganesha/src/os/freebsd/xattr.c

## Purpose
This file maps Linux-style file-descriptor extended attribute APIs onto FreeBSD `extattr_*_fd()` calls for the VFS FSAL.

## Important APIs, Types, and Functions
It implements `fgetxattr()`, `fsetxattr()`, `flistxattr()`, and `fremovexattr()`. All operations use `EXTATTR_NAMESPACE_SYSTEM`. `fsetxattr()` probes existing attribute state with `extattr_get_fd()` and honors Linux-like `XATTR_REPLACE` and `XATTR_CREATE` flags before calling `extattr_set_fd()`.

## Control Flow
Get/list/remove directly call the corresponding FreeBSD extattr function. Set clears `errno`, attempts to get the existing attribute into a stack buffer, returns an error for replace-if-missing or create-if-existing cases, and otherwise sets the value.

## State and Persistence Behavior
The functions persist extended attribute changes on the target file descriptor. No process-global state is stored.

## Dependencies and Integration Points
It depends on `os/freebsd/xattr.h`, FreeBSD `<sys/extattr.h>`, `errno`, and xattr flag definitions. FSAL code can call Linux-compatible xattr names while building on FreeBSD.

## Risks and Edge Cases
`fsetxattr()` returns positive `ENOATTR`/`EEXIST` values instead of `-1` with `errno` set, unlike normal POSIX-style APIs. The existence probe passes the caller's value `size` with a fixed `EXTATTR_MAXNAMELEN` stack buffer; if `size` exceeds 255, this can overflow `buff`. It compares `attr_size != size` to infer missing attributes, which confuses existing attributes whose size differs from the new value. Namespace choice is fixed to system and may not match user xattr expectations.

## Test Signals
FreeBSD xattr tests should cover get/set/list/remove, create-only existing, replace-only missing, attributes larger than 255 bytes, replacing with different-sized values, and errno/return-value compatibility with Linux callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/xattr.c -->
