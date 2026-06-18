<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_once.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_once.c

## Purpose
Provides process-wide one-time initialization for POSIX builds.

## Important APIs, Types, and Functions
`__wt_once(void (*init_routine)(void))` wraps `pthread_once` with a static `pthread_once_t`.

## Control Flow
Every call passes the same static once control object to `pthread_once`, so the first successful call invokes the supplied routine and subsequent calls return without invoking it again.

## State and Persistence Behavior
The only state is the process-local `pthread_once_t`; nothing is persisted. Because the control object is shared, this wrapper supports a single global initialization site, not one distinct once state per caller.

## Dependencies and Integration Points
Used by code that requires platform-independent one-time initialization. Relies on pthread semantics for thread safety and memory ordering.

## Risks and Edge Cases
Passing different routines after the first call will not run them. Errors are returned directly from `pthread_once` and should be rare.

## Test Signals
Concurrent multi-thread invocation should run the routine exactly once and propagate pthread errors if injected.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_once.c -->
