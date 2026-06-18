<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_thread.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_thread.c

## Purpose
Provides POSIX thread creation, join, identity, process ID, and Linux thread-name support.

## Important APIs, Types, and Functions
`__wt_thread_create`, `__wt_thread_join`, `__wt_thread_id`, `__wt_thread_str`, and `__wt_process_id`; Linux builds also use internal thread-name setup.

## Control Flow
Thread creation initializes attributes, sets joinable state, creates the pthread, optionally names it from session/thread metadata, and destroys attributes. Join calls `pthread_join`. Thread ID is derived from `pthread_self` into `uintmax_t`; string form formats that ID. Process ID returns `getpid`.

## State and Persistence Behavior
Creates and joins OS threads but writes no WiredTiger persistent state. Thread naming affects OS diagnostics only.

## Dependencies and Integration Points
Used by background services, worker threads, and diagnostics. Integrates with session names and portable type `wt_thread_t`.

## Risks and Edge Cases
Thread ID formatting assumes `pthread_t` can be represented as copied bytes/number on supported platforms. Naming truncation is platform-limited. Attribute setup failures must not leak attributes.

## Test Signals
Thread lifecycle tests, join error/failure injection, thread ID uniqueness, and Linux name visibility tests are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_thread.c -->
