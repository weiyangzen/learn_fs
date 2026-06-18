# sources/storage-engines/wiredtiger/src/include/session_inline.h

## Purpose
Provides diagnostic-only inline checks enforcing WiredTiger's contract that a non-default session is used by only one thread at a time, while allowing re-entrant API calls by the owning thread.

## Important APIs, Types, And Functions
- `__wt_single_thread_check_start(WT_SESSION_IMPL *)` records or verifies the owning thread on API entry.
- `__wt_single_thread_check_stop(WT_SESSION_IMPL *)` decrements re-entry depth and releases ownership when the outermost API call exits.

## Control Flow
In non-diagnostic builds both functions are no-ops. In diagnostic builds, start obtains the current thread id, reads the current owner with relaxed atomics, and, if this is a non-default session not already owned by the same thread, tries to take `thread_check.lock`. Failure asserts with detailed session state. On success it stores the current owner and increments `entry_count`. Stop decrements `entry_count`; when it reaches zero for non-default sessions, it clears the owner and unlocks.

## State And Persistence Behavior
This logic mutates diagnostic runtime fields under `WT_SESSION_IMPL.thread_check`. It does not persist data, but it protects the broader invariant that session-local fields can be treated as thread-local by many lock macros and subsystems.

## Dependencies And Integration Points
Depends on diagnostic build flags, thread id retrieval, spinlock trylock/unlock, relaxed atomic load/store, session names/last operations, API call depth, and data-handle names. It supports assumptions used in schema lock flags, operation tracking, cursor/session state, and error handling.

## Risks
The checks are compiled out in production, so they detect but do not prevent misuse in release builds. The default session intentionally permits concurrent access because it is used during connection initialization and error paths. Relaxed atomics are chosen to avoid hiding bugs; correctness relies on the spinlock for ownership transitions.

## Test Signals
Diagnostic tests should cover same-thread re-entry, cross-thread sequential use, concurrent cross-thread assertion, default-session exemption, owner clearing on final stop, and assertion messages containing useful active operation/session details.
