# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_futex.cpp

## Purpose
Tests WiredTiger futex wait/wake wrappers for single wake, timeout, waking one of multiple waiters, wake-all, and multiple separate wakes.

## Important APIs, Types, And Functions
`waiter` wraps `__wt_futex_wait`, records return, errno, and wake value, and classifies errors/timeouts/awakened/spurious wakeups. `wake_signal`, `wake_one`, and `wake_all` describe `__wt_futex_wake` calls. `futex_tester` manages futex word state, threads, waiter creation, delayed wake, joining, and result inspection.

## Control Flow
Each test creates a tester, starts waiter threads on an expected futex value with timeout, optionally delays and sends wake signals, joins threads, and checks outcomes. Inspection allows spurious wakeups but requires no lost signals or unexpected timeout counts.

## State And Persistence Behavior
State is an in-memory futex word and thread-local waiter results. No persistence. Atomic store uses Windows `InterlockedExchange` or GCC `__atomic_store_n`.

## Dependencies And Integration Points
Depends on threading, chrono, algorithms, Catch2, and `wt_internal.h`. It exercises platform futex abstraction behavior.

## Risks And Edge Cases
Concurrency tests are timing-sensitive and account for spurious wakeups. They guard against lost signals, incorrect wake values, wake-all not reaching all waiters, and timeouts that should have been wakes.

## Test Signals
`inspect_waiters` must return `AsExpected`. Non-timeout errors, unexpected timeout counts, or unmatched wake values fail the test.
