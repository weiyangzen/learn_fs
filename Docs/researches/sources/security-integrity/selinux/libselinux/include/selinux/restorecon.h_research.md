# sources/security-integrity/selinux/libselinux/include/selinux/restorecon.h

## Purpose
`restorecon.h` declares high-level relabeling APIs for restoring filesystem contexts according to SELinux file-context specifications, including recursive and parallel relabeling, digest/xattr management, exclude lists, alternate roots, and counters.

## Important APIs, types, and functions
Primary APIs are `selinux_restorecon()`, `selinux_restorecon_parallel()`, `selinux_restorecon_set_sehandle()`, `selinux_restorecon_default_handle()`, `selinux_restorecon_set_exclude_list()`, `selinux_restorecon_set_alt_rootpath()`, `selinux_restorecon_xattr()`, `selinux_restorecon_get_skipped_errors()`, and `selinux_restorecon_get_relabeled_files()`. Flags control no-change mode, recursion, progress, realpath, xdev, syslog, match logging, digest behavior, conflict handling, user/role changes, error counting, relabel counting, and multilink skipping. `struct dir_xattr` reports digest xattr scan/delete results.

## Control flow
Callers optionally set a custom selabel handle, exclude list, or alternate root, then call restorecon on a path with flags. The library lazily creates a default file-label handle when needed. Xattr-specific calls scan or delete `security.sehash` digests and return a linked result list.

## State and persistence behavior
The restorecon subsystem uses process-global configuration for the default handle, exclude list, alternate root, and counters. Persistent effects can include changing file security labels, writing/removing digest xattrs, logging changes, and reading mount information.

## Dependencies and integration points
The header depends on `selinux/label.h` and system types. It integrates with file-context backends, filesystem traversal, xattrs, syslog, mount filtering, and command-line tools such as `restorecon` and `setfiles`.

## Risks and edge cases
Global restorecon settings and counters are sensitive to threading and call ordering. Flag combinations can change semantics significantly, especially no-change/counting/progress/digest modes. Recursive relabeling can cross large trees unless `XDEV` or excludes are set. Digest read/write may require `CAP_SYS_ADMIN`. Alternate root handling must avoid accidentally relabeling the host tree.

## Test signals
Tests should cover dry-run and real relabeling, recursive traversal, xdev and exclude behavior, custom handles, alternate roots, digest skip/ignore/delete paths, conflict-error handling, error counting, relabeled-file counters, parallel execution, and hard-link multilink skipping.
