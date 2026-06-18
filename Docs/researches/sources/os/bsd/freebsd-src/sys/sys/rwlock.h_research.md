# File Research: sources/os/bsd/freebsd-src/sys/sys/rwlock.h

Read completely: 299 lines.

## Purpose
Defines FreeBSD kernel reader/writer lock state encoding, fast-path macros, public lock API wrappers, sysinit helpers, and assertions.

## Main Elements
- Documents packed `rw_lock` word layout: read/write bit, waiter bits, write-spinner bit, writer-recursed bit, writer owner pointer or reader count.
- Defines lock flag masks, owner/read-count extraction, one-reader increment, unlocked, and destroyed encodings.
- Provides atomic fast-path macros for write lock/unlock and inline non-debug write acquisition/release.
- Declares internal initialization, destruction, sysinit, ownership, read/write lock/unlock, trylock, upgrade, downgrade, hard-path, and assertion functions.
- Maps public macros to debug/no-debug and inline/non-inline implementations depending on `LOCK_DEBUG` and `RWLOCK_NOINLINE`.
- Provides `rw_unlock`, `rw_sleep`, `rw_initialized`, `RW_SYSINIT_FLAGS`, and `RW_SYSINIT`.
- Defines init option flags and invariant assertion aliases.

## Dependencies And Integration
Used throughout the kernel for sleepable reader/writer synchronization. Integrates with lock objects, WITNESS, lockstat, PCPU/current-thread state, atomic operations, sleep, and `kern_rwlock.c`.

## Risk Notes
The packed-state protocol is subtle. Waiter bits, recursive writer state, reader counts, and owner pointers must be manipulated only through the lock API; callers must include `sys/lock.h` first so `LOCK_DEBUG` is defined.
