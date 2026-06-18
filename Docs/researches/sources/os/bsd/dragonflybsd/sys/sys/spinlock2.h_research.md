# File Research: sources/os/bsd/dragonflybsd/sys/sys/spinlock2.h

This kernel-only inline header implements fast-path DragonFly spinlock operations, shared spinlocks, upgrades, initialization, and update-counter read/retry support.

Key responsibilities:
- Rejects userland inclusion.
- Includes kernel systm/thread/globaldata and machine atomic/cpufunc headers.
- Declares global `pmap_spin`.
- Declares contested-path helpers:
  - `spin_trylock_contested()`
  - `_spin_lock_contested()`
  - `_spin_lock_shared_contested()`
- Defines public macros that pass `__func__` as the wait/identity string.
- Defines `spin_trylock()`:
  - enters critical section
  - increments per-CPU spinlock count
  - CASes lock from 0 to 1
  - falls back to contested trylock
  - records debug lock stack if enabled
- Defines `spin_held()`.
- Defines exclusive lock/unlock fast paths:
  - `_spin_lock_quick()`
  - `_spin_lock()`
  - `spin_unlock_quick()`
  - `spin_unlock()`
  - `spin_unlock_any()`
- Defines shared lock/unlock fast paths:
  - `_spin_lock_shared_quick()`
  - `_spin_lock_shared()`
  - `spin_unlock_shared_quick()`
  - `spin_unlock_shared()`
- Defines `spin_lock_upgrade_try()`.
- Defines `spin_init()` and `spin_uninit()`.
- Defines update-counter access API:
  - `spin_access_start()`
  - `spin_access_end()`
  - `spin_lock_update()`
  - `spin_unlock_update()`
- Defines non-lock-integrated update-counter API:
  - `spin_access_start_only()`
  - `spin_access_check_inprog()`
  - `spin_access_end_only()`
  - `spin_lock_update_only()`
  - `spin_unlock_update_only()`

Important invariants:
- All successful lock acquisitions enter a raw critical section and increment `gd_spinlocks`.
- Unlock paths decrement `gd_spinlocks` and exit the critical section after clearing the lock.
- Shared spinlocks cache `SPINLOCK_SHARED` when count reaches zero for faster subsequent shared locks.
- Exclusive conflict handling can convert multiply-held shared locks to exclusive waiting state; shared unlock comments warn about this.
- Update counter uses odd values to mark modification in progress and even values for stable snapshots.
- `spin_access_start()` acquires a shared spinlock if an update is in progress, avoiding dirtying cachelines in the normal read path.

Research notes:
- This is a highly concurrency-sensitive header; memory barriers and atomic operations are integral to correctness.
