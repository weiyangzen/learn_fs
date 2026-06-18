<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/setfilecon.c -->
# sources/security-integrity/selinux/libselinux/utils/setfilecon.c

## Purpose
CLI for setting the same SELinux context on one or more paths.

## Important APIs, Types, And Functions
Loops over `path...` and calls `setfilecon(path, context)`.

## Control Flow
Requires `context path...`; exits on first failure.

## State And Persistence Behavior
Writes `security.selinux` xattrs through translated context setter.

## Dependencies And Integration Points
Thin wrapper over `src/setfilecon.c`.

## Risks And Test Signals
Test multiple paths, invalid contexts, permission denied, unsupported filesystems, partial failure behavior, and symlink-following semantics.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/setfilecon.c -->
