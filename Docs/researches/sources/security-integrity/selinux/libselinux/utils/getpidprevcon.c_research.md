<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getpidprevcon.c -->
# sources/security-integrity/selinux/libselinux/utils/getpidprevcon.c

## Purpose
Prints the previous SELinux context for a process ID.

## Important APIs, Types, And Functions
Parses one PID, calls `getpidprevcon()`, prints and frees the result.

## Control Flow
Same argument and error pattern as `getpidcon`.

## State And Persistence Behavior
Read-only `/proc/<pid>/attr/prev` access.

## Dependencies And Integration Points
Wraps previous-context support in `procattr.c`.

## Risks And Test Signals
Test invalid/nonexistent PIDs, processes with no previous context, permission errors, and translation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getpidprevcon.c -->
