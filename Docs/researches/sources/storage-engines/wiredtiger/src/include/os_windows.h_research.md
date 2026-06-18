# sources/storage-engines/wiredtiger/src/include/os_windows.h

## Purpose
Defines Windows-specific threading, synchronization, calling-convention, POSIX-compatibility, and fsync aliases for WiredTiger.

## Important APIs, Types, And Functions
- `wt_cond_t`, `wt_mutex_t`, and `wt_sem_t` map to `CONDITION_VARIABLE`, `CRITICAL_SECTION`, and `HANDLE`.
- `wt_thread_t` stores a creation flag, unused name index, and Windows thread handle.
- `WT_THREAD_CALLBACK`, `WT_THREAD_RET`, and `WT_THREAD_RET_VALUE` match `_beginthreadex`.
- `WT_CDECL` maps to `__cdecl`.
- Defines `struct timespec` for older MSVC, POSIX-like `u_int`, `u_char`, `u_long`, and optionally `ssize_t`.
- Maps `fsync` to `_commit`.

## Control Flow
No functions are implemented here; it establishes types and macros consumed by common threading and filesystem code.

## State And Persistence Behavior
Thread, mutex, condition, and semaphore state is runtime state. Mapping `fsync` to `_commit` affects durability behavior for Windows file descriptors.

## Dependencies And Integration Points
Depends on Windows headers included before or nearby in the platform build. Used by mutex, thread, semaphore, and OS file code. It must align with `msvc.h` atomic and barrier definitions.

## Risks
Thread callback signatures must exactly match `_beginthreadex`; mismatches can corrupt stack/calling conventions. `ssize_t` typedef is guarded to avoid Python/header conflicts. The older-MSVC `timespec` definition must not conflict with newer toolchains.

## Test Signals
Windows CI should compile thread callbacks, run condition/mutex/semaphore tests, validate fsync aliasing through file sync tests, and build with supported MSVC versions around the `timespec`/`ssize_t` guards.
