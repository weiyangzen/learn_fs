<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_priv.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_priv.c

## Purpose
Provides the Windows implementation of privilege detection.

## Important APIs, Types, and Functions
`__wt_has_priv(void)` currently returns false.

## Control Flow
There is no probing; Windows builds report no special POSIX-style privilege state.

## State and Persistence Behavior
No state changes.

## Dependencies and Integration Points
Satisfies the portable privilege-check API for callers shared with POSIX.

## Risks and Edge Cases
This does not detect Administrator elevation, service accounts, privileges, or token changes. Callers needing Windows-specific security must not rely on this alone.

## Test Signals
Compatibility tests should assert the stable false result; security-sensitive Windows behavior needs separate coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_priv.c -->
