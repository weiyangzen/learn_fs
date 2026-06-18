# sources/security-integrity/selinux/libselinux/src/fgetfilecon.c

Purpose: Reads the SELinux file context xattr from an open file descriptor.

Important APIs/types/functions: `fgetfilecon_raw()` reads `security.selinux` and returns a raw context string. `fgetfilecon()` translates it. `fgetxattr_wrapper()` emulates `O_PATH` support through `/proc/self/fd/<fd>` when `fgetxattr()` returns `EBADF`.

Control flow: raw function starts with `INITCONTEXTLEN + 1`, retries with exact xattr size on `ERANGE`, treats zero-length attributes as `ENOTSUP`, and returns the byte count on success. Public wrapper returns translated string length including NUL when translation succeeds.

State and persistence: read-only xattr access; caller owns returned memory.

Dependencies and integration: depends on Linux xattrs, `O_PATH`, `/proc/self/fd`, `XATTR_NAME_SELINUX`, and raw/trans conversion helpers.

Risks and test signals: tests should cover normal fd, O_PATH fd, ERANGE resize, empty xattr, ENOENT-to-EBADF mapping for proc fallback, and translation failure.
