# sources/storage-engines/wiredtiger/src/os_linux/os_futex.c

## Purpose
Implements WiredTiger futex wait/wake primitives on Linux using the `SYS_futex` syscall.

## Important APIs, Types, and Functions
`__wt_futex_wait` wraps `FUTEX_WAIT_PRIVATE`. `__wt_futex_wake` wraps `FUTEX_WAKE_PRIVATE` and supports `WT_FUTEX_WAKE_ONE` or `WT_FUTEX_WAKE_ALL`.

## Control Flow
Wait asserts a positive microsecond timeout, converts it to `timespec`, and calls `syscall(SYS_futex, addr, FUTEX_WAIT_PRIVATE, expected, &timeout, NULL, 0)`. On success it loads the wake value atomically. Wake computes a wake count of `1` or `INT_MAX`, stores the wake value, calls the futex wake syscall, and returns zero for any nonnegative syscall result or the negative syscall value on error.

## State and Persistence Behavior
State is the futex word in memory; no durable state is involved.

## Dependencies and Integration Points
The file depends on Linux futex headers, syscall ABI, timespec conversion, and atomic stores/loads. It supports higher-level spin/condition abstractions used throughout WiredTiger.

## Risks and Edge Cases
The wait wrapper returns raw negative syscall results rather than mapping through `errno`, so callers must follow the expected convention. Timeout and spurious wake behavior are inherited from futex semantics. Wake-all uses `INT_MAX`, which is conventional but assumes waiter counts never need exact reporting.

## Test Signals
Linux synchronization tests should cover timeout, wake-one, wake-all, expected-value mismatch, spurious wake tolerance, and stress under many waiters.
