<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_mtx_sem.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_mtx_sem.c

## Purpose
Implements WiredTiger semaphore primitives on Windows.

## Important APIs, Types, and Functions
`__wt_semaphore_init`, `__wt_semaphore_destroy`, `__wt_semaphore_post`, and `__wt_semaphore_wait`.

## Control Flow
Init creates a Windows semaphore with the requested initial count and max `INT32_MAX`. Destroy closes the handle and clears the structure. Post releases one count. Wait blocks indefinitely with `WaitForSingleObject` and maps failures.

## State and Persistence Behavior
Only kernel semaphore state and the `WT_SEMAPHORE` structure change; no persistent state is written.

## Dependencies and Integration Points
Used where POSIX builds use semaphores or equivalent synchronization. Error messages use Windows formatting.

## Risks and Edge Cases
Counts are limited to `INT32_MAX`. Wait has no timeout/cancel path here. Destroying while waiters exist is unsafe and must be prevented by callers.

## Test Signals
Producer/consumer semaphore tests, post/wait ordering, destroy failure injection, and count-limit checks are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_mtx_sem.c -->
