# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_objcache.c

This file implements DragonFlyBSD's magazine-based object cache. It provides low-overhead per-CPU object reuse backed by a shared depot of full and empty magazines, plus creation, destruction, reclaim, malloc-backed helpers, and sysctl statistics.

Core structures:
- `struct magazine` stores a stack of object pointers with `rounds` and `capacity`.
- `struct magazinedepot` is the shared cluster-level depot containing full and empty magazine lists, allocation limits, waiters, and a spinlock.
- `struct percpu_objcache` stores each CPU's loaded and previous magazines plus counters for gets, puts, allocations, exhaustion, and waits.
- `struct objcache` ties constructors/destructors, backend alloc/free callbacks, per-cluster depots, and per-CPU caches together.
- `struct objcache_desc` tracks named caches globally for sysctl reporting.

Important functions:
- `objcache_create()` allocates the descriptor and cache, chooses magazine capacity from `cluster_limit`, `nom_cache`, and CPU count, creates two magazines per CPU, seeds the depot with empty magazines, and links the cache into `allobjcaches`.
- `objcache_create_simple()` and `objcache_create_mbacked()` build malloc-backed caches using `objcache_malloc_alloc/free`.
- `objcache_get()` is the hot allocation path. It first pops from the CPU loaded magazine, then previous magazine, then swaps with a depot full magazine, and finally calls the backend allocator if under limit. It can sleep when exhausted and `M_WAITOK` without `M_NULLOK` is requested.
- `objcache_put()` returns to the loaded or previous magazine, cycles full magazines through the depot, or destroys the object if no empty magazine is available.
- `objcache_dtor()` bypasses reuse for invalid objects and immediately returns allocation capacity to the depot.
- `mag_purge()`, `maglist_disassociate()`, `maglist_purge()`, `objcache_reclaimlist()`, and `objcache_destroy()` implement reclaim and teardown.
- `sysctl_ocstats()` emits `struct objcache_stats` entries for each live cache.

Concurrency and lifecycle:
- Per-CPU hot paths use `crit_enter()` rather than a global lock.
- Depot exchange is serialized by `depot->spin`.
- The global cache list is protected by `objcachelist_spin`.
- Destructors/free callbacks may block, so depot lists are disassociated before purge where needed.

Filesystem/storage relevance:
- This is a core allocator primitive used by kernel subsystems, including VFS and storage code, to amortize frequent fixed-size allocations without global contention.

Notable risk/quirk:
- NUMA support is stubbed as `MAXCLUSTERS 1`, `myclusterid 0`, and `CLUSTER_OF(obj) 0`; the depot design anticipates clusters but currently behaves as single-cluster.
