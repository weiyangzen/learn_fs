# File Research: sources/os/bsd/freebsd-src/sys/sys/sx.h

## Purpose
`sx.h` defines the kernel sleepable shared/exclusive lock API and lock-word encoding.

## Main Interfaces
- Lock state flags include shared/exclusive state, shared waiters, exclusive waiters, write spinner, recursion, waiter mask, owner extraction, and shared-holder count encoding.
- Declares initialization, destruction, try-lock, lock, unlock, upgrade, downgrade, assertion, and DDB owner-chain routines.
- `SX_SYSINIT` and `SX_SYSINIT_FLAGS` register static sx locks with SYSINIT/SYSUNINIT.
- Public macros expose `sx_xlock`, `sx_xlock_sig`, `sx_xunlock`, `sx_slock`, `sx_slock_sig`, `sx_sunlock`, `sx_try_*`, `sx_downgrade`, `sx_unlock`, `sx_sleep`, and `sx_assert`.

## Implementation Notes
The comments compare sx locks with rwlocks: sx uses sleep queues and lacks priority propagation, while rwlocks use turnstiles. Non-debug kernels inline exclusive lock/unlock fast paths with atomic compare-and-set and defer contention to hard routines. `_STANDALONE` builds provide no-op boot-loader versions.

## Dependencies and Constraints
Includes `sys/_lock.h` and `sys/_sx.h`; kernel builds also include pcpu, lock profiling/stat, and machine atomics. Kernel use requires `LOCK_DEBUG` from `sys/lock.h`.
