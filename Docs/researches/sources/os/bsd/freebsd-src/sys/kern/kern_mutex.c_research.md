# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_mutex.c

Read completely: 1371 lines.

## Purpose
Implements the machine-independent parts of FreeBSD mutexes, including sleep mutexes, spin mutexes, adaptive spinning, turnstile blocking, lock-class integration, thread lock handling, assertions, initialization/destruction, DDB display, and system mutex bootstrap.

## Main Elements
- Defines lock classes `lock_class_mtx_sleep` and `lock_class_mtx_spin`.
- Provides exported function forms of inline mutex operations: `__mtx_lock_flags()`, `__mtx_unlock_flags()`, `__mtx_lock_spin_flags()`, `__mtx_trylock_spin_flags()`, and `__mtx_unlock_spin_flags()`.
- `_mtx_trylock_flags_int()` implements trylock with recursion handling for sleep mutexes.
- `__mtx_lock_sleep()` handles contested sleep mutex acquisition, recursion, adaptive spinning on running owners, turnstile wait setup, waiters marking, lock profiling, and DTrace lockstat hooks.
- `_mtx_lock_spin_cookie()` handles contested spin mutex acquisition with spinlock enter/exit balancing and indefinite-spin detection.
- `_thread_lock()` and `thread_lock_flags_()` acquire a thread's current spin lock while tolerating lock migration.
- `thread_lock_block()`, `thread_lock_unblock()`, `thread_lock_block_wait()`, and `thread_lock_set()` support temporary thread-lock replacement.
- `__mtx_unlock_sleep()` handles recursion unwind, uncontested release, and contested wakeup through turnstiles.
- `__mtx_assert()` validates ownership, recursion, and non-ownership assertions.
- `_mtx_init()`, `mtx_sysinit()`, and `_mtx_destroy()` initialize and destroy mutexes with witness/profile flags.
- `mutex_init()` initializes turnstiles, `Giant`, `blocked_lock`, proc0 locks, device mutexes, and locks Giant during early boot.
- `mtx_spin_wait_unlocked()` and `mtx_wait_unlocked()` wait until spin or sleep mutexes become unlocked.
- DDB support prints mutex class, state, owner, and recursion count.

## Dependencies And Integration
Integrates with lock classes, witness, turnstiles, scheduler state, thread structures, spinlock sections, lock profiling, DTrace lockstat, HWPMC soft hooks, KTR, DDB, devfs mutexes, and early kernel bootstrap.

## Risk Notes
The file encodes core locking invariants: sleep mutexes cannot be used as spin mutexes, spin locks must balance interrupt state, recursion requires explicit flags, and thread locks can migrate while being acquired. Adaptive spinning depends on owner thread run state. Long-held spin mutexes panic after repeated indefinite checks.
