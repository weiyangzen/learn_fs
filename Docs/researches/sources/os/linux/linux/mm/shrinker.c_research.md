# File Research: sources/os/linux/linux/mm/shrinker.c

Implements the core shrinker registry and execution engine used by reclaim to ask subsystem caches how many objects are reclaimable and to scan them. It supports global shrinkers, NUMA-aware shrinkers, memcg-aware shrinkers, deferred scan accounting, debugfs naming, and RCU-safe registration/removal.

Key responsibilities:
- Maintains the global `shrinker_list` protected by `shrinker_mutex` for mutation and RCU for reclaim-time iteration.
- Allocates/frees `struct shrinker` objects through `shrinker_alloc()` and `shrinker_free()`.
- Registers shrinkers with `shrinker_register()` and exposes names through shrinker debugfs support.
- Computes scan targets in `do_shrink_slab()` from freeable object counts, reclaim priority, previous deferred work, shrinker seek cost, and batch size.
- Tracks deferred scan counts per shrinker, per NUMA node, and when applicable per memcg shrinker id.
- Implements global slab shrinking via RCU list traversal and shrinker refcounts.
- Implements memcg slab shrinking by using per-memcg bitmaps to call only shrinkers that have objects charged in that memcg/node.
- Allocates, expands, frees, and reparents per-memcg `shrinker_info` structures.
- Allocates memcg-aware shrinker ids with an IDR and expands every online memcg's shrinker bitmap/deferred arrays as ids grow.

Important behavior:
- `do_shrink_slab()` first calls `count_objects()`. `SHRINK_EMPTY` and zero mean no scan work; otherwise it computes `delta` from priority and `seeks`, adds deferred work, caps scan work to twice freeable objects, and calls `scan_objects()` in batches.
- Shrinkers with `seeks == 0` are scanned aggressively because their objects are assumed cheap to recreate.
- Unused scan work is returned to deferred accounting so later reclaim can pick it up without over-scanning concurrent shrinkers.
- Global shrinking uses `shrinker_try_get()` under RCU, drops RCU while running potentially sleeping callbacks, reacquires RCU before `shrinker_put()`, and then continues iteration safely.
- Memcg shrinking walks bitmap units. If a shrinker reports `SHRINK_EMPTY`, the bit is cleared, a memory barrier pairs with `set_shrinker_bit()`, and the shrinker is sampled one more time to avoid losing a concurrent object addition.
- `set_shrinker_bit()` is the producer-side hook for memcg-aware shrinkers; it sets the per-memcg/node bit after a barrier so reclaim sees newly queued objects.
- `shrinker_free()` drops the registration reference, waits for in-flight lookups to finish through a completion, removes list/debugfs/id state under `shrinker_mutex`, and frees memory after an RCU grace period.

Dependencies:
- Uses memcg internals, RCU, IDR, mutexes, completions/refcounts, atomic deferred counters, vmscan tracepoints, debugfs helper functions from `shrinker_debug.c`, NUMA node ids, and shrinker callback contracts from `linux/shrinker.h`.

Notable risks:
- Lifetime rules are delicate: reclaim may run shrinker callbacks while unregister is waiting, so refcount/completion/RCU ordering must remain exact.
- Per-memcg shrinker-info expansion copies old unit pointers and publishes new arrays under RCU; readers must reacquire RCU after sleeping callbacks because the array may have been replaced.
- Deferred scan accounting is approximate and concurrent by design; incorrect capping or missed updates can cause either reclaim latency or cache growth.
- Memcg-aware shrinkers depend on producers setting bits when objects appear. If a subsystem forgets to call `set_shrinker_bit()`, memcg reclaim may skip reclaimable objects.
