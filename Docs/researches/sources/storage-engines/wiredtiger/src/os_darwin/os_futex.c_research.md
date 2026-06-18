# sources/storage-engines/wiredtiger/src/os_darwin/os_futex.c

## Purpose
Implements WiredTiger futex wait/wake primitives on Darwin using Apple's private ulock APIs.

## Important APIs, Types, and Functions
`__wt_futex_wait` waits on a `WT_FUTEX_WORD` matching an expected value with a microsecond timeout. `__wt_futex_wake` stores a wake value and wakes either one waiter or all waiters depending on `WT_FUTEX_WAKE`.

## Control Flow
Wait converts microseconds to nanoseconds and calls `__ulock_wait2` with `UL_COMPARE_AND_WAIT_SHARED | ULF_NO_ERRNO`. Nonnegative returns and `-EFAULT` are treated as success after loading the wake value. Other negative returns are converted to `errno` and `-1`. Wake stores `wake_val`, calls `__ulock_wake`, ignores `-ENOENT`, and maps `-EINTR`/`-EAGAIN` to `errno=EINTR` and `-1`.

## State and Persistence Behavior
State is the futex word in memory. There is no persistence.

## Dependencies and Integration Points
It depends on `<ulock.h>`, Apple private API semantics, atomic loads/stores, and WiredTiger condition/lock primitives built on futexes.

## Risks and Edge Cases
The API is private and poorly documented. `-EFAULT` may mean the page was paged out rather than an invalid address, so the code intentionally reloads the address. The ulock wake value argument is wider than the futex word and is assumed unused unless `ULF_WAKE_THREAD` is set.

## Test Signals
Darwin concurrency tests should cover timed waits, wake-one, wake-all, no-waiter wake, signal interruption behavior, and stress under paging/memory pressure.
