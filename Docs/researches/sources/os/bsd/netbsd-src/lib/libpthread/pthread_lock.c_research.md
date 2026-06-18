# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_lock.c

This file implements internal libpthread simple-lock primitives. It provides two `pthread_lock_ops` tables: one using restartable atomic sequences (RAS) and one using machine atomic simple locks. The global `pthread__lock_ops` defaults to RAS for early single-threaded startup safety, then `pthread__lockprim_init` chooses atomic operations on multiprocessor/concurrent execution or installs RAS on uniprocessor systems when available.

`pthread__spinlock_slow` is the contended path used through the lock ops table. It repeatedly checks the lock, pauses with SMT hints for a configured number of spins, tries again when the lock appears free, and yields when spinning is exhausted. The spin count comes from `PTHREAD_NSPINS`, defaults to 64 on concurrent systems, and 1 on single-concurrency systems.

Integration points: underlies public spinlocks and internal per-thread cached lock ops in `struct __pthread_st`. Risks are architecture-specific RAS support, tuning sensitivity of spin/yield behavior, and startup ordering before full threading initialization.
