<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/unsetfiles/unsetfiles.c -->
# sources/security-integrity/selinux/policycoreutils/unsetfiles/unsetfiles.c

## Purpose
Removes `security.selinux` extended attributes from files or directory trees, but only when SELinux is not enabled.

## Important APIs, Types, And Functions
Key functions are `usage()`, recursive `unset()`, and `main()`. It uses `lgetxattr`, `lremovexattr`, `openat`, `fdopendir`, `readdir`, `dirfd`, `fstat`, `stat`, `asprintf`, and `is_selinux_enabled()`.

## Control Flow
`main()` parses dry-run, recursive, verbose, and same-filesystem options, rejects execution on SELinux-enabled systems, optionally records the root device for `-x`, and calls `unset()` for each path. `unset()` checks for an SELinux xattr and either reports or removes it. In recursive mode it opens directories without following symlinks, enforces the device boundary when requested, iterates children, builds full paths for reporting/xattr calls, and recurses.

## State And Persistence
Without `-n`, it persistently removes SELinux labels from filesystem objects. It does not follow symlinked directories for traversal.

## Dependencies And Integration Points
Useful for converting or cleaning filesystems outside active SELinux. It depends on Linux xattrs and libselinux status.

## Risks And Edge Cases
It intentionally refuses to run when SELinux is enabled. Errors are reported but do not accumulate into a nonzero exit code for individual failed paths. Full paths are used for xattr operations while `openat` protects traversal.

## Test Signals
Test SELinux-enabled refusal, dry-run output, recursive traversal, symlink handling, device-boundary skipping, verbose ENODATA/ENOTSUP reporting, and failure exit behavior expectations.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/unsetfiles/unsetfiles.c -->
