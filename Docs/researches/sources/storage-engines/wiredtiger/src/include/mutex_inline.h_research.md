# sources/storage-engines/wiredtiger/src/include/mutex_inline.h

## Purpose
Implements inline spinlock lifecycle, acquisition, ownership checks, unlock behavior, and tracked statistic updates across GCC atomics, pthread mutexes, adaptive pthread mutexes, and MSVC critical sections.

## Important APIs, Types, And Functions
- `WT_SPIN_SESSION_ID_SAFE` maps a possibly null session to a valid tracking id.
- `__spin_init_internal` initializes common spinlock metadata.
- `__wt_spin_init`, `__wt_spin_destroy`, `__wt_spin_trylock`, `__wt_spin_lock`, and `__wt_spin_unlock` have platform-specific implementations.
- `__wt_spin_locked`, `__wt_spin_owned`, and `__wt_spin_unlock_if_owned` inspect or conditionally release ownership.
- `WT_ASSERT_SPINLOCK_OWNED` validates ownership in diagnostic assertions.
- `WT_SPIN_INIT_TRACKED` and `WT_SPIN_INIT_SESSION_TRACKED` attach stat offsets.
- `__wt_spin_lock_track` and `__wt_spin_trylock_track` update acquisition counts and wait-time stats.

## Control Flow
GCC spinlocks use `__atomic_test_and_set`, pause loops up to `WT_SPIN_COUNT`, then yield. Pthread variants initialize and use mutex APIs, optionally adaptive, panicking on unexpected lock/unlock errors. MSVC uses critical sections. All successful acquisitions record `session_id`; unlock resets it before releasing. Tracked locks measure elapsed clock time, increment connection and optional session stat counters, and separate application versus internal sessions.

## State And Persistence Behavior
The functions mutate in-memory lock state and lock ownership metadata only. They affect persistent safety by guarding shared data structures. Stat counters are runtime diagnostic/performance state.

## Dependencies And Integration Points
Depends on platform locking APIs, atomic helpers, session IDs, stats macros, `WT_SESSION_INTERNAL`, clocks, panic/error handling, and `mutex.h` layout. Used by schema/metadata locks, page locks, scratch locks, RTS queues, and any code requiring short critical sections.

## Risks
Ownership tracking is diagnostic and must stay synchronized with actual lock state. Pthread lock/unlock failures panic, so incorrect lifecycle handling is severe. The GCC spin path can consume CPU under contention; callers should keep critical sections small. Null-session lock calls are supported but produce `WT_SESSION_ID_NULL` ownership, which limits ownership assertions.

## Test Signals
Signals include platform CI for every spinlock backend, lock contention stress tests, ownership assertion tests, stat counter validation, null-session acquisition paths, destroy-after-init behavior, and deadlock/race testing under TSan.
