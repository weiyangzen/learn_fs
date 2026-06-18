<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_thread.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_thread.c

## Purpose
Provides Windows thread creation, join, thread ID/string, and process ID helpers.

## Important APIs, Types, and Functions
`__wt_thread_create`, `__wt_thread_join`, `__wt_thread_id`, `__wt_thread_str`, and `__wt_process_id`.

## Control Flow
Create starts a thread with `_beginthreadex` and stores the handle/id. Join waits indefinitely, closes the handle, and clears the thread object. ID helpers use `GetCurrentThreadId`; process ID uses `GetCurrentProcessId`.

## State and Persistence Behavior
Creates OS threads and releases handles; no persistent state. Correct handle closure prevents kernel object leaks.

## Dependencies and Integration Points
Used by background services and diagnostics through portable `wt_thread_t`.

## Risks and Edge Cases
Thread start failures map CRT/Windows errors. Join must only run on valid joinable handles. Thread functions must match `_beginthreadex` calling conventions.

## Test Signals
Thread lifecycle tests, join failure injection, handle leak checks, and ID formatting tests are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_thread.c -->
