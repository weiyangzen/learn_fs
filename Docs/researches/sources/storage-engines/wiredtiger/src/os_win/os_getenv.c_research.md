<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_getenv.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_getenv.c

## Purpose
Provides Windows environment-variable retrieval with WiredTiger-owned output storage.

## Important APIs, Types, and Functions
`__wt_getenv` uses `getenv_s` sizing and value retrieval.

## Control Flow
The function initializes `*envp` to NULL, queries the required length, returns absent for errors or zero-length values, allocates that size, then calls `getenv_s` again to populate the buffer.

## State and Persistence Behavior
No persistent state. Returned memory is allocated through WiredTiger and must be freed by callers.

## Dependencies and Integration Points
Used by portable environment configuration paths. Depends on MSVC secure CRT behavior and WiredTiger allocation.

## Risks and Edge Cases
The environment can change between sizing and retrieval. Empty values are treated as absent. CRT errors are silently converted to absence in the sizing step.

## Test Signals
Tests should cover absent, empty, non-empty, long variables, and injected allocation/retrieval failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_getenv.c -->
