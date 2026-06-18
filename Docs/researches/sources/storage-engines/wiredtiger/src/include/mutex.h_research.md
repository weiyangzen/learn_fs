# sources/storage-engines/wiredtiger/src/include/mutex.h

## Purpose
Declares WiredTiger synchronization primitives: condition variables, semaphores, read/write locks, and spin locks, along with tracked initialization macros for statistics.

## Important APIs, Types, And Functions
- `struct __wt_condvar` stores a mutex, condition variable, waiter count, and adaptive wait-duration state.
- `struct __wt_semaphore` wraps platform semaphores with a debug name.
- `struct __wt_rwlock` stores ticket-style read/write state in a shared 64-bit union, stat offsets, condition variables for readers/writers, and optional TSan synchronization.
- `WT_RWLOCK_INIT_TRACKED` and `WT_RWLOCK_INIT_SESSION_TRACKED` initialize locks and populate connection/session statistic offsets.
- `struct __wt_spinlock` abstracts GCC bool spinlocks, pthread mutex/adaptive mutexes, or Windows critical sections, plus ownership session id, stat offsets, and initialization state.

## Control Flow
This header is mostly structure layout. Tracked init macros call lower-level initialization, then compute stat-array offsets from generated stat fields so inline acquisition code can update counters without knowing concrete stat structures.

## State And Persistence Behavior
All state is in-memory synchronization state. `waiters`, rwlock ticket fields, spinlock session id, and initialization flags are shared across threads. No fields are persistent, but correctness protects persistent metadata and data structures elsewhere.

## Dependencies And Integration Points
Depends on platform typedefs (`wt_mutex_t`, `wt_cond_t`, `wt_sem_t`), stats offset macros, `WT_SESSION_IMPL`, connection stats, and spinlock type configuration. Used by connection locks, schema locks, table/handle locks, cache/session locks, RTS queues, and many internal data structures.

## Risks
Structure layout must match inline implementations in `mutex_inline.h` and platform OS headers. Stat offsets use `int16_t`; generated stat layouts must remain within range. Spinlock type selection changes performance and semantics. Misusing spinlocks for long critical sections can harm latency.

## Test Signals
Concurrency tests should cover rwlock read/write exclusion, condition variable signaling and timeout behavior, semaphore wakeups, stat tracking, initialization/destruction idempotence, and all configured `SPINLOCK_TYPE` variants.
