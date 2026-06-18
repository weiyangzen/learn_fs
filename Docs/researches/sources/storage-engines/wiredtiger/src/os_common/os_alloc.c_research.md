# sources/storage-engines/wiredtiger/src/os_common/os_alloc.c

## Purpose
Wraps allocation, reallocation, duplication, and free operations with WiredTiger error handling, statistics, optional debug behavior, and optional Windows TCMalloc integration.

## Important APIs, Types, and Functions
Functions include exported `__wt_calloc`, `__wt_malloc`, `__wt_realloc`, `__wt_realloc_noclear`, `__wt_memdup`, `__wt_strndup`, and exported `__wt_free_int`. Private `__realloc_func` implements the shared realloc path.

## Control Flow
Allocation functions defensively NULL the output pointer before trying allocation, increment stats when a session exists, and return `WT_RET_MSG` on failure. Realloc asserts growth, optionally forces malloc/copy/free under `WT_CONN_DEBUG_REALLOC_MALLOC`, clears new memory unless using the noclear variant, and updates the tracked allocation size. Free reads a pointer-to-pointer, sets it to NULL before freeing, and increments free stats.

## State and Persistence Behavior
No durable state is written. Runtime state includes connection memory allocation/grow/free counters and the caller-owned allocation-size variable. The zeroing contract is important because some WiredTiger structures assume newly grown memory is cleared.

## Dependencies and Integration Points
This is the base allocation layer for nearly all WiredTiger modules. It depends on session stats, debug flags, errno mapping, explicit overwrite, and macros that pass pointer addresses into `__wt_free`.

## Risks and Edge Cases
Functions must support `NULL` sessions. Realloc requires callers to pass correct old allocation size when clearing memory; otherwise assertions catch mismatches. `__wt_memdup` with zero length would violate `__wt_malloc`'s nonzero assertion. `__wt_free_int` reduces but cannot eliminate double-free races if callers lack synchronization.

## Test Signals
Allocator failure injection, debug `realloc_malloc`, memory stats, zeroed growth checks, string duplication with embedded NUL handling through `__wt_strndup`, and sanitizer runs are useful signals.
