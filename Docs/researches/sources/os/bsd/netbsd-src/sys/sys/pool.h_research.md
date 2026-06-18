# File Research: sources/os/bsd/netbsd-src/sys/sys/pool.h

## Purpose
Defines NetBSD fixed-size pool allocator and pool-cache interfaces, including sysctl statistics, allocator backends, pool descriptors, cache groups, per-CPU cache state, flags, and kernel APIs.

## Main API
- Sysctl snapshot: `struct pool_sysctl`.
- Exposed internals under `__POOL_EXPOSE`: `struct pool_allocator`, `struct pool`, `struct pool_cache`, `pool_cache_group`, `pool_cache_cpu_t`.
- Flags: `PR_WAITOK`, `PR_NOWAIT`, `PR_WANTED`, `PR_PHINPAGE`, `PR_LIMITFAIL`, `PR_RECURSIVE`, `PR_NOTOUCH`, `PR_NOALIGN`, `PR_LARGECACHE`, `PR_GROWING`, `PR_ZERO`, `PR_USEBMAP`, `PR_PSERIALIZE`.
- Global allocators: `pool_allocator_kmem`, `pool_allocator_nointr`, `pool_allocator_meta`.
- Pool APIs: `pool_init`, `pool_destroy`, `pool_get`, `pool_put`, `pool_reclaim`, `pool_prime`, `pool_setlowat`, `pool_sethiwat`, `pool_sethardlimit`, `pool_drain`.
- Cache APIs: `pool_cache_init`, `pool_cache_bootstrap`, `pool_cache_destroy`, `pool_cache_get_paddr`, `pool_cache_put_paddr`, `pool_cache_invalidate`, `pool_cache_reclaim`, limit/prime/drain helpers.
- Diagnostics: `pool_printit`, `pool_printall`, `pool_chk`, `pool_whatis`.

## Dependencies
Kernel internals use parameters, mutexes, condition variables, queues, trees, callback support, and optional pool configuration.

## Risks and Notes
Pool locking deliberately does not cover backend page allocator calls. `PR_PSERIALIZE` indicates delayed safe reclamation requirements. Cache group sizing and per-CPU state are cache-line sensitive, and diagnostic fields change behavior under redzone/quarantine configurations.
