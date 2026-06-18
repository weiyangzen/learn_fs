<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getfilecon.c -->
# sources/security-integrity/selinux/libselinux/utils/getfilecon.c

## Purpose
Prints SELinux file contexts for one or more paths.

## Important APIs, Types, And Functions
Loops over operands, calls `getfilecon()`, prints `path<TAB>context`, and frees each context.

## Control Flow
Requires at least one path and exits on the first failure.

## State And Persistence Behavior
Read-only xattr/context access.

## Dependencies And Integration Points
Thin CLI wrapper for translated file-context reads.

## Risks And Test Signals
Test multiple paths, missing files, permission errors, translated contexts, and paths containing tabs/newlines.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getfilecon.c -->
