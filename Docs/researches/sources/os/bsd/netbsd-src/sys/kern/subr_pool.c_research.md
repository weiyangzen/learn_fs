# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_pool.c

## Purpose
Implements NetBSD's general fixed-size kernel pool allocator and the higher-level pool cache object allocator. It manages pages split into fixed-size items, per-CPU magazines/cache groups, low/high/hard water marks, reclaim/drain paths, diagnostics, KMSAN/KASAN/redzone integration, and `kern.pool` sysctl statistics.

## Main Entry Points
- Pool lifecycle and allocation: `pool_subsystem_init()`, `pool_init()`, `pool_destroy()`, `pool_get()`, `pool_put()`, `pool_prime()`, `pool_setlowat()`, `pool_sethiwat()`, `pool_sethardlimit()`, `pool_reclaim()`, `pool_drain()`, `pool_totalpages()`, and `pool_totalpages_locked()`.
- Pool cache lifecycle and operations: `pool_cache_init()`, `pool_cache_bootstrap()`, `pool_cache_destroy()`, `pool_cache_bootstrap_destroy()`, `pool_cache_get_paddr()`, `pool_cache_put_paddr()`, `pool_cache_invalidate()`, `pool_cache_reclaim()`, and setter/stat wrappers.
- Backend allocators: `pool_page_alloc()`, `pool_page_free()`, metadata-page variants, standard allocator structs, and large-object allocator selection.
- Diagnostics: `pool_printall()`, `pool_printit()`, `pool_chk()`, optional DDB `pool_whatis()`, and `pool_sysctl()`.

## Control Flow And State
Pools keep pages on empty, full, and partially full lists. A page header may live in the page (`PR_PHINPAGE`) or in a private page-header pool; free items are tracked either by bitmap (`PR_USEBMAP`) or linked list. `pool_get()` enforces context and wait flags, checks hard limits, grows the pool if `pr_curpage` is empty, removes an item, updates page lists and counters, optionally catches up to low water marks, fills redzones, marks KMSAN origins, and zeroes on `PR_ZERO`. `pool_put()` optionally quarantines the object, checks redzones/freecheck, returns it to a bitmap/list, wakes waiters, and frees whole pages when above limits.

Pool caches layer per-CPU current/previous cache groups over a backing pool. Fast paths run at `splvm()` and avoid locks when current/previous groups have space. Slow get pulls a full group from global lists or allocates/constructs a new object. Slow put obtains an empty group or destructs the object immediately. Invalidation broadcasts xcalls so CPUs transfer local groups to global lists, then destructs cached objects. Lockless cache-group lists use atomic CAS and `pcg_dummy` as a temporary busy marker.

## Integration Points
Depends on UVM/VMEM for page allocation, CPU/xcall APIs, atomics, sysctl, DDB, lockdebug/freecheck, KMSAN, KASAN/ASAN, pserialize barriers for `PR_PSERIALIZE`, and kernel logging. It is itself foundational for many kernel subsystems and has bootstrap pools for page headers and cache metadata.

## Risks And Notes
This file is heavily invariant-driven. Misconfiguring item size, alignment, `PR_NOTOUCH`, `PR_PSERIALIZE`, or allocator page size can break page-header lookup or object lifetime guarantees. Cache invalidation is expensive and prohibited in interrupt context. `POOL_QUARANTINE` disables caching through `POOL_NOCACHE`. Redzone/KASAN modes avoid passive-serialization pools because freed objects may need to remain valid until a barrier. The `kern.pool` sysctl takes references while copying records out to avoid racing destruction.
