# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_mtxpool.c

Read completely: 186 lines.

## Purpose
Provides shared pools of mutexes selected by pointer hash or round-robin allocation, allowing subsystems to associate short-term leaf locks with objects without embedding a mutex in each object.

## Main Elements
- Defines `struct mtx_pool` with size/mask/shift metadata and a variable-length mutex array.
- Global `mtxpool_sleep` is created during `SI_SUB_MTX_POOL_DYNAMIC`.
- `mtx_pool_find()` maps an arbitrary pointer to a pool mutex using Fibonacci hashing.
- `mtx_pool_create()` validates power-of-two size, allocates the pool, and initializes all mutexes.
- `mtx_pool_destroy()` destroys pool mutexes and frees the pool.
- `mtx_pool_alloc()` returns the next mutex from the pool using an intentionally racy round-robin cursor.

## Dependencies And Integration
Uses kernel malloc, mutex initialization/destruction, cache-line alignment, KTR includes, and SYSINIT. Intended for leaf-level sleep mutex use where structural overhead would be too high.

## Risk Notes
Pool mutexes should be treated as leaf locks because unrelated objects may hash to the same lock and pool-to-pool ordering is not stable. `mtx_pool_next` is intentionally unprotected, which is acceptable only because exact round-robin fairness is not required.
