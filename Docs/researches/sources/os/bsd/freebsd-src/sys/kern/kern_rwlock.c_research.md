# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_rwlock.c

Read completely: 1582 lines.

## Purpose
Implements FreeBSD's machine-independent sleepable reader/writer lock core, including adaptive spinning, turnstile blocking, recursive writer support, upgrades/downgrades, lock-class integration, assertions, and DDB inspection.

## Main Elements
- Defines `lock_class_rw` with lock, trylock, unlock, assert, owner, and DDB hooks.
- Stores state in the packed `rw_lock` word: unlocked/read-count state, write owner thread pointer, reader/writer wait flags, writer spinner flag, and writer-recursed bit.
- `_rw_init_flags()` initializes WITNESS/profiling/recursion options; `_rw_destroy()` verifies unlocked/non-recursed state and marks destroyed locks.
- `_rw_wlock_cookie()` fast-acquires an unlocked lock by installing the current thread pointer, otherwise enters `__rw_wlock_hard()`.
- `__rw_try_wlock_int()` attempts nonblocking writer acquisition, including recursive writer acquisition when `LO_RECURSABLE` is set.
- `_rw_wunlock_cookie()` releases write ownership through inline fast unlock or `__rw_wunlock_hard()` for recursion and waiter cases.
- `__rw_can_read()` and `__rw_rlock_try()` implement reader admission policy: ordinary readers can enter only when there is no writer/writer-wait/spinner state, while recursive readers already holding a read lock may enter to avoid self-deadlock.
- `__rw_rlock_hard()` handles contended readers, including adaptive spinning on running writers or active readers, read-waiter flag management, turnstile sleeping, lockstat/KDTRACE accounting, and priority owner tracking.
- `__rw_try_rlock_int()` performs nonblocking reader count increments when the lock is in readable state.
- `__rw_runlock_try()` decrements reader count on the fast path; `__rw_runlock_hard()` handles last-reader release with waiters and wakes either shared or exclusive turnstile queues.
- `__rw_wlock_hard()` handles contended writers, recursive writer entry, adaptive spinning on running owners or reader counts, writer-spinner flag management, write-waiter flag setup, turnstile sleeping, and lock profiling.
- `__rw_wunlock_hard()` unwinds recursive writers or releases a contended write lock, preserving the appropriate waiter flag and broadcasting to either reader or writer waiters.
- `__rw_try_upgrade_int()` atomically upgrades a sole reader to writer, claiming the turnstile when waiter flags are preserved.
- `__rw_downgrade_int()` converts a writer to one reader, wakes compatible readers when no writer waiters are pending, and disowns or unpends the turnstile as needed.
- `__rw_assert()` validates read/write/locked/unlocked/recursive state using WITNESS when available and fallback state checks otherwise.
- DDB support prints unlocked/destroyed/read/write state, writer thread identity, recursion count, and waiter categories.

## Dependencies And Integration
Integrated with turnstiles and priority propagation, scheduler running-state checks, adaptive lock-delay tuning, WITNESS, lockstat/KDTRACE, HWPMC lock-failure hooks, lock profiling, DDB, and per-thread read-lock counters.

## Risk Notes
The packed-state protocol is subtle: waiter bits, spinner bits, reader counts, and owner pointers must be updated with the right acquire/release ordering. Fairness and latency depend on adaptive spinning heuristics and the choice of which turnstile queue to wake. Upgrades only succeed for a single reader and must preserve waiter ownership correctly.
