# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ccms.c

## Purpose
Implements the local locking portion of HAMMER2's CCMS cache coherency state, currently providing shared/exclusive thread locks over `ccms_cst_t`.

## Key Elements
- `ccms_cst_init()` zeroes the cache-state structure and initializes its HAMMER2 spinlock; `ccms_cst_uninit()` asserts no active holders.
- `ccms_thread_lock()` acquires shared or exclusive state, allowing recursive exclusive acquisition by the owning thread and sleeping on the CST when incompatible locks or upgrades are present.
- `ccms_thread_lock_nonblock()` mirrors normal locking but returns `EBUSY` instead of sleeping.
- `ccms_thread_lock_temp_release()` and `ccms_thread_lock_temp_restore()` temporarily release and reacquire the caller's held state.
- `ccms_thread_lock_upgrade()` converts a shared lock to exclusive by incrementing `upgrade`, dropping the caller's shared count, and waiting for other shared holders to drain.
- `ccms_thread_lock_downgrade()` returns an upgraded exclusive lock back to shared state and wakes blocked waiters.
- `ccms_thread_unlock()` releases recursive exclusive, final exclusive, or shared locks, waking sleepers when the final blocking condition clears.
- `ccms_thread_unlock_upgraded()` releases a lock that had been upgraded from shared or falls back to normal unlock for exclusive-origin locks.
- `ccms_thread_lock_owned()` and `ccms_thread_lock_setown()` expose/check exclusive ownership.

## Dependencies
Uses DragonFly kernel primitives (`curthread`, `ssleep`, `wakeup`, `hz`, `panic`, `KKASSERT`) and HAMMER2 spin wrappers from `hammer2.h`/`hammer2_ccms.h`. `LOCKENTER` and `LOCKEXIT` are external lock-debug/accounting macros.

## Behavior/Risks
- The implementation is strictly local locking, not the full distributed MESI-like protocol described in the header comments.
- Exclusive locks are recursive only for the owning thread; shared locks wait behind pending upgrades to prevent upgrade starvation.
- The code depends on callers pairing upgrade/downgrade/unlock APIs correctly; incorrect pairing corrupts `upgrade`, `count`, or `td` state and will assert or panic.
