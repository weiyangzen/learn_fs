# sources/storage-engines/wiredtiger/src/include/posix.h

## Purpose
Defines POSIX-platform compatibility types and constants for WiredTiger threading, file flags, and numeric limits.

## Important APIs, Types, And Functions
- Includes `<sys/statvfs.h>`.
- Supplies `ULLONG_MAX`, `LLONG_MAX`, and `LLONG_MIN` if the system headers did not.
- Defines `O_BINARY` as `0` on POSIX.
- Defines `wt_cond_t` as `pthread_cond_t` and `wt_mutex_t` as `pthread_mutex_t`.
- Defines `wt_thread_t` with creation flag, name index, and `pthread_t` id.
- Defines thread callback macros `WT_THREAD_CALLBACK`, `WT_THREAD_RET`, and `WT_THREAD_RET_VALUE`.
- Defines Linux `WT_THREAD_NAME_MAX_LEN` as 16.
- Defines `WT_CDECL` as empty.

## Control Flow
No executable logic is present. The macros/types allow common code to compile across POSIX and Windows.

## State And Persistence Behavior
Thread and synchronization fields are runtime state only. `O_BINARY` being zero documents that POSIX does not distinguish binary/text open modes.

## Dependencies And Integration Points
Depends on pthread and POSIX headers included by the platform build. Used by mutex/thread code, file open logic, and cross-platform function declarations.

## Risks
Thread name length is Linux-specific and must be enforced by callers using `pthread_setname_np`. Fallback numeric limits must match platform width assumptions. `WT_THREAD_CALLBACK` includes a lint suppression because the macro intentionally produces a function declarator shape.

## Test Signals
POSIX CI should compile thread callback declarations, run thread creation/join/naming tests, mutex/condition tests, and file open tests that include `O_BINARY`.
