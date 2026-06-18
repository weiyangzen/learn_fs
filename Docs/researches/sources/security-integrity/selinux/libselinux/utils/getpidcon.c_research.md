<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getpidcon.c -->
# sources/security-integrity/selinux/libselinux/utils/getpidcon.c

## Purpose
Prints the current SELinux context for a process ID.

## Important APIs, Types, And Functions
Parses one `pid`, calls `getpidcon()`, prints and frees the returned context.

## Control Flow
Usage, invalid pid text, and API failure return distinct exits.

## State And Persistence Behavior
Read-only procattr access.

## Dependencies And Integration Points
Wraps `procattr.c` PID context support.

## Risks And Test Signals
Test invalid PID strings, pid `0`/negative, nonexistent process, permission denied, and translated contexts.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getpidcon.c -->
