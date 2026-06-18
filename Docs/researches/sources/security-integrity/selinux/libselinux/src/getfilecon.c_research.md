# sources/security-integrity/selinux/libselinux/src/getfilecon.c

Purpose: Reads a path's SELinux file context xattr following symlinks.

Important APIs/types/functions: `getfilecon_raw()` calls `getxattr()` for `security.selinux`; `getfilecon()` translates the returned raw context.

Control flow: starts with `INITCONTEXTLEN + 1`, retries with exact size after `ERANGE`, treats zero-length attributes as `ENOTSUP`, returns raw byte count on success, and public wrapper returns translated string length plus NUL.

State and persistence: read-only xattr access.

Dependencies and integration: used by file-labeling and restorecon-style callers.

Risks and test signals: tests should cover ERANGE, empty xattr, missing xattr, symlink-following semantics, translation failure, and memory cleanup.
