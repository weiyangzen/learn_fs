<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/linux/acl.c -->
# sources/user-network-fs/nfs-ganesha/src/os/linux/acl.c

## Purpose
This Linux file supplies non-standard POSIX ACL file-descriptor helpers when the platform lacks `acl_get_fd_np()` or `acl_set_fd_np()`, especially for default ACLs.

## Important APIs, Types, and Functions
Under `#ifndef HAVE_ACL_GET_FD_NP`, `acl_get_fd_np(int fd, acl_type_t type)` returns `acl_get_fd(fd)` for `ACL_TYPE_ACCESS`, otherwise builds `/proc/self/fd/<fd>` and calls `acl_get_file(path, type)`. Under `#ifndef HAVE_ACL_SET_FD_NP`, `acl_set_fd_np(int fd, acl_t acl, acl_type_t type)` similarly uses `acl_set_fd()` for access ACLs and `/proc/self/fd/<fd>` plus `acl_set_file()` for other types.

## Control Flow
Both functions validate `fd >= 0`, format the procfs fd path with `snprintf()`, reject truncation by setting `errno = EINVAL`, and delegate to libacl functions. Get returns `NULL` on error; set returns `-1` on local validation errors or the libacl return code.

## State and Persistence Behavior
Get has no persistent side effect. Set persists ACL changes to the file referenced by the descriptor. No module-global state is kept.

## Dependencies and Integration Points
It depends on `os/acl.h`, libacl APIs, `PATH_MAX`, `/proc/self/fd`, `errno`, and `snprintf()`. It supports FSAL ACL code that wants descriptor-based ACL operations even when libacl lacks the `_np` variants.

## Risks and Edge Cases
The default ACL path fallback depends on procfs being mounted and accessible. Path-based `/proc/self/fd/<fd>` operations can behave differently for some special descriptors or deleted files. The source includes `<stdio.h>` but relies on `PATH_MAX` from headers pulled indirectly through `os/acl.h`; portability depends on that include chain.

## Test Signals
Linux tests should compile with and without native `_np` functions, get/set access ACLs directly, get/set default ACLs through `/proc/self/fd`, handle invalid fds, and run in environments with procfs unavailable or restricted if supported.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/linux/acl.c -->
