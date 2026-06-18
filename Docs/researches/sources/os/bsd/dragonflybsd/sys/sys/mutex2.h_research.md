# File Research: sources/os/bsd/dragonflybsd/sys/sys/mutex2.h

Inline fast paths and utility functions for DragonFlyBSD mutexes.

Key responsibilities:
- Provides initialization and deinitialization helpers for mutexes and mutex links.
- Provides exclusive/shared lock operations with optional link, timeout, quick, try, and recursion support.
- Provides exclusive spinlock/spinunlock helpers that enter and exit hard critical sections and update per-CPU spinlock counts.
- Provides downgrade and upgrade-try helpers.
- Provides unlock variants for generic, exclusive, and shared releases.
- Provides lock-state predicates, owner predicates, lock reference count, and temporary release/restore helpers.

Important behavior:
- Fast paths use `atomic_cmpset_int()` for uncontended acquisition and release.
- Exclusive locks set `mtx_owner` to `curthread`; shared locks do not.
- Spinlocking enters a critical section before attempting acquisition and must be paired with `mtx_spinunlock()`.
- Unlock handles exclusive, shared, blocking, and spin-acquired mutexes via the same lock word and slow-path fallback.
- `mtx_lock_temp_release()` records only whether the prior state was exclusive, then unlocks and later restores exclusive or shared mode.

Dependencies:
- Includes `mutex.h`, `thread2.h`, `globaldata.h`, and machine atomics.
- Depends on `curthread`, `mycpu`, critical-section helpers, CPU fences, `KKASSERT`, and slow-path `_mtx_*` functions.

Notable risks:
- Correct pairing of spinlock/spinunlock is required to balance critical sections and `gd_spinlocks`.
- `mtx_notlocked_ex()` returns `(mtx_lock & MTX_EXCLUSIVE) != 0`, which contradicts its comment saying it returns true if not exclusively locked.
- Temporary release/restore only restores mode, not recursion depth.
- Atomic fast paths and owner updates must remain ordered with backend slow paths.
