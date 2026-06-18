<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_getenv.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_getenv.c

## Purpose
Provides the POSIX implementation of `__wt_getenv`, returning a WiredTiger-owned copy of a non-empty environment variable.

## Important APIs, Types, and Functions
`__wt_getenv(WT_SESSION_IMPL *, const char *, const char **)` wraps C `getenv` and `__wt_strdup`.

## Control Flow
The output is initialized to `NULL`. If `getenv(variable)` returns a non-NULL string with length greater than zero, the value is duplicated through the session allocator and returned; otherwise the call succeeds with `*envp == NULL`.

## State and Persistence Behavior
No persistent state is written. The returned value is heap/session allocated, decoupling callers from process environment storage and leaving ownership with WiredTiger memory management.

## Dependencies and Integration Points
Used by platform-independent configuration paths that need environment variables without exposing raw libc pointers. Error behavior depends on `__wt_strdup`.

## Risks and Edge Cases
Empty environment variables are intentionally treated as absent. Callers must free the duplicated result. Environment mutation by other threads is outside this wrapper's control.

## Test Signals
Tests should cover missing, empty, and non-empty variables, including allocator failure injection.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_getenv.c -->
