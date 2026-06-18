# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_pthread.h

## Purpose
Provides PerconaFT-style pthread wrapper types and inline helpers used by the Toku locktree code embedded in RocksDB. It normalizes mutexes, condition variables, rwlocks, thread-local keys, joins, detaches, and thread exit behind `toku_*` names while preserving optional performance-schema instrumentation and debug ownership checks.

## Important APIs, Types, And Functions
The main public types are `toku_mutex_t`, `toku_cond_t`, `toku_pthread_rwlock_t`, `toku_mutex_aligned_t`, and aliases such as `toku_pthread_t`, `toku_pthread_key_t`, and `toku_timespec_t`. Important helpers include `toku_mutex_init`, `toku_mutex_destroy`, `toku_mutex_lock_with_source_location`, `toku_mutex_trylock_with_source_location`, `toku_mutex_unlock`, `toku_cond_init`, `toku_cond_wait_with_source_location`, `toku_cond_timedwait_with_source_location`, `toku_cond_signal`, `toku_cond_broadcast`, and thread-specific wrappers. Macros inject `__FILE__` and `__LINE__` into lock and wait calls.

## Control Flow
Mutex lock and condition wait operations start instrumentation, call the underlying pthread primitive, end instrumentation, assert success, then update debug fields when enabled. Condition waits temporarily clear debug ownership before the pthread wait releases the mutex and restore ownership after wake-up. Destructor and initializer wrappers maintain instrumentation handles alongside native pthread objects.

## State And Persistence Behavior
All state is in memory. `toku_mutex_t` and `toku_cond_t` store native pthread objects plus optional instrumentation and debug metadata. There is no durable persistence. Correct lifetime is manual: callers must initialize before use and destroy after no threads can access the object.

## Dependencies And Integration Points
Depends on `pthread.h`, `toku_portability.h`, assertion macros, and Toku instrumentation functions such as `toku_instr_mutex_*` and `toku_instr_cond_*`. It is used broadly by the range-tree lock library for locktree manager, lock requests, and wait queues.

## Risks And Edge Cases
`toku_mutex_trylock_with_source_location` calls `pthread_mutex_lock` rather than `pthread_mutex_trylock`, so its name is misleading and any caller expecting nonblocking behavior would block. Debug assertions depend on strict single-owner use and can fire if native pthread objects are manipulated outside these wrappers. Adaptive mutex initialization is platform-dependent, with musl and Apple falling back to default mutexes.

## Test Signals
Signals are indirect through range-locking tests and locktree unit coverage. Debug builds can catch invalid unlocks, destroyed locked mutexes, and condition waits without held mutexes. Sanitizer or deadlock tests should pay attention to the misleading trylock wrapper.
