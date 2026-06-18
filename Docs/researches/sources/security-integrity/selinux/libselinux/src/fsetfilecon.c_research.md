# sources/security-integrity/selinux/libselinux/src/fsetfilecon.c

Purpose: Sets the SELinux file context xattr on an open file descriptor.

Important APIs/types/functions: `fsetfilecon_raw()` sets raw `security.selinux`; `fsetfilecon()` translates input to raw. `fsetxattr_wrapper()` emulates `O_PATH` support via `/proc/self/fd/<fd>` after `EBADF`.

Control flow: raw setter writes `strlen(context) + 1` bytes. If `setxattr` reports `ENOTSUP`, it reads the current context and treats the operation as success if the requested context already matches, preserving the original error otherwise.

State and persistence: modifies file xattr state when supported.

Dependencies and integration: depends on xattr syscalls, `/proc/self/fd`, raw/trans conversion, and `fgetfilecon_raw()` for ENOTSUP equality fallback.

Risks and test signals: high impact because it relabels files. Tests should cover O_PATH fallback, ENOTSUP same-context success, ENOTSUP different-context failure, translation failure, and context string NUL-length write.
