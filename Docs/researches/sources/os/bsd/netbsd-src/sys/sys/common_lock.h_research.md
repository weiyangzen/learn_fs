# File Research: sources/os/bsd/netbsd-src/sys/sys/common_lock.h

Implements machine-dependent simple spinlock primitives using compiler atomic builtins, intended for ports that use the shared implementation.

Key content:
- Lock state tests: `__SIMPLELOCK_LOCKED_P`, `__SIMPLELOCK_UNLOCKED_P`.
- Direct state setters/initializers.
- Spin acquisition via `__atomic_exchange_n(..., __ATOMIC_ACQUIRE)`.
- Try-lock and release via `__atomic_store_n(..., __ATOMIC_RELEASE)`.

Important behavior:
- Assumes `__cpu_simple_lock_t`, `__SIMPLELOCK_LOCKED`, and `__SIMPLELOCK_UNLOCKED` are supplied by machine headers.
- Clear/set/init currently use direct stores under `#if 1`, with atomic-store alternatives retained but disabled.
- Provides low-level synchronization semantics used below higher-level kernel locks.
