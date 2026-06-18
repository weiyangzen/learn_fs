<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setfilecon.c -->
# sources/security-integrity/selinux/libselinux/src/setfilecon.c

## Purpose
Sets an SELinux context on a path following normal xattr semantics.

## Important APIs, Types, And Functions
`setfilecon_raw()` writes `security.selinux` using `setxattr()`. `setfilecon()` translates a context to raw form first.

## Control Flow
Like `lsetfilecon_raw()`, it treats `ENOTSUP` as success only if the current raw file context already equals the requested one.

## State And Persistence Behavior
Persists the `security.selinux` xattr on the target path. The translated wrapper allocates and frees the raw context.

## Dependencies And Integration Points
Uses setrans translation, xattr APIs, `getfilecon_raw()`, `freecon()`, and `policy.h`.

## Risks And Test Signals
Test symlink-following expectations, unsupported filesystems, identical/different labels, translation failure, invalid contexts, and permission errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setfilecon.c -->
