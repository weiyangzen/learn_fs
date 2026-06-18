# sources/sync-backup/rsync/lib/sysacls.c

## Purpose
`sysacls.c` is rsync's portability layer for filesystem ACL operations. It normalizes several platform-specific ACL APIs behind the `sys_acl_*` interface declared in `sysacls.h`, allowing the higher-level ACL synchronization code to enumerate, create, validate, set, delete, and free ACLs without knowing whether the platform uses POSIX.1e, Tru64, Solaris/UnixWare, HPUX, IRIX, AIX, or macOS ACL semantics.

## Important APIs, Types, and Functions
The exported surface includes `sys_acl_get_entry()`, `sys_acl_get_tag_type()`, `sys_acl_get_info()`, `sys_acl_get_file()`, `sys_acl_get_fd()`, `sys_acl_init()`, `sys_acl_create_entry()`, `sys_acl_set_info()`, `sys_acl_set_access_bits()`, `sys_acl_valid()`, `sys_acl_set_file()`, `sys_acl_set_fd()`, `sys_acl_delete_def_file()`, `sys_acl_free_acl()`, and `no_acl_syscall_error()`. `SAFE_FREE()` is a small local helper. Most functions have separate conditional implementations selected by `HAVE_POSIX_ACLS`, `HAVE_TRU64_ACLS`, `HAVE_UNIXWARE_ACLS`, `HAVE_SOLARIS_ACLS`, `HAVE_HPUX_ACLS`, `HAVE_IRIX_ACLS`, `HAVE_AIX_ACLS`, or `HAVE_OSX_ACLS`.

## Control Flow
The file compiles only under `SUPPORT_ACLS`. POSIX and Tru64 paths are thin wrappers over native calls, with permission bits converted to rsync's read/write/execute bit mask. Solaris, UnixWare, and HPUX allocate synthetic `SMB_ACL_T` buffers, fetch access and default entries with `acl()` loops that handle `ENOSPC`, split or combine default ACL entries for directories, and sort before validation or setting. HPUX adds runtime probing for the `acl()` system call and a local `hpux_acl_sort()` fallback. AIX maps its ACL linked-list structures into rsync's simplified POSIX-like entries and fabricates owner, group, and other entries. macOS maps NFSv4-style extended ACL allow/deny entries and UUID qualifiers into rsync's tag and bit encoding.

## State and Persistence
ACL objects are transient heap allocations, but `sys_acl_set_file()` and `sys_acl_delete_def_file()` persist changes to filesystem metadata. HPUX caches the successful presence check in a static flag. AIX mutates entry access bits while converting between shifted mode-style bits and AIX ACL bits, so callers must not assume entries remain immutable across set operations.

## Dependencies and Integration Points
The file depends on `rsync.h`, `sysacls.h`, platform ACL headers, libc allocation, `stat()`, and platform APIs such as `acl_get_file()`, `acl()`, `statacl()`, `chacl()`, membership UUID conversion, and `acl_set_file()`. It is consumed by rsync ACL preservation code that expects POSIX-like traversal and permission extraction. `no_acl_syscall_error()` feeds higher-level fallback behavior when a filesystem or platform reports unsupported ACLs.

## Risks
The main risk is semantic loss across incompatible ACL models, especially AIX deny entries and macOS extended ACL bits. Several branches use historical platform APIs and custom memory layouts with manual resizing and sorting. Directory updates on Solaris/HPUX rewrite combined access plus default ACL sets, which can race with external ACL changes. Some file-descriptor ACL functions are compiled out, so path-based operations are the real supported path in several branches.

## Test Signals
Strong signals are platform matrix builds with ACL support enabled, round-trip tests preserving named user/group entries, default directory ACLs, mask recalculation, unsupported filesystem errors, and macOS allow/deny ACLs. Regression tests should check that `EINVAL`, `ENOTSUP`, and `ENOSYS` are recognized as no-ACL conditions where intended, and that setting access ACLs on directories does not drop existing default ACLs.
