<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_priv.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_priv.c

## Purpose
Detects whether the process is running with elevated or changed effective POSIX privileges.

## Important APIs, Types, and Functions
`__wt_has_priv` compares real/effective UID and GID via `getuid`, `geteuid`, `getgid`, and `getegid`.

## Control Flow
Returns true when either UID or GID differs, false otherwise.

## State and Persistence Behavior
No persistent state. The result can influence security-sensitive configuration decisions.

## Dependencies and Integration Points
Integrated into portable security checks that should behave differently for setuid/setgid processes.

## Risks and Edge Cases
It detects changed effective IDs, not every possible privilege mechanism such as capabilities or platform ACLs.

## Test Signals
Unit tests can mock or run under controlled IDs; integration should verify behavior in setuid/setgid-like environments where available.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_priv.c -->
