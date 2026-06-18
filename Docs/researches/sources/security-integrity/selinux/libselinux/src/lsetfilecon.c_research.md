<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/lsetfilecon.c -->
# sources/security-integrity/selinux/libselinux/src/lsetfilecon.c

## Purpose
Sets an SELinux file context on a path without following the final symlink.

## Important APIs, Types, And Functions
`lsetfilecon_raw()` writes the `security.selinux` xattr through `lsetxattr()`. `lsetfilecon()` translates a possibly human-readable context to raw form with `selinux_trans_to_raw_context()` before calling the raw setter.

## Control Flow
The raw setter writes `strlen(context) + 1` bytes. If `lsetxattr()` returns `ENOTSUP`, it reads the current raw context and treats the operation as success when the requested context already matches.

## State And Persistence Behavior
The only persistence is the file xattr. The compatibility path avoids failing no-op writes on unsupported xattr backends when the existing label is already correct.

## Dependencies And Integration Points
Depends on `policy.h` for `XATTR_NAME_SELINUX`, translation support from setrans, and `lgetfilecon_raw()`/`freecon()`.

## Risks And Test Signals
Test symlink targets, unsupported filesystems, identical/different existing labels, null/invalid contexts, and translated versus raw contexts. The ENOTSUP fallback is security-sensitive because it must not mask a requested label change.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/lsetfilecon.c -->
