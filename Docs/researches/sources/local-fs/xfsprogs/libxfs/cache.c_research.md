# File Research: sources/local-fs/xfsprogs/libxfs/cache.c

Generic pthread-protected hash/MRU cache used by libxfs buffer targets.

Key responsibilities:
- Creates/destroys caches with hash buckets and MRU lists.
- Looks up, allocates, references, dereferences, purges, flushes, and reports cache nodes.
- Enforces maximum cache size with `cache_shake`.
- Parks dirty/unflushable nodes on a special dirty MRU priority.
- Supports optional cache operations for hash, compare, alloc, flush, release, bulk release, get, and put.

Important behavior:
- Cache miss allocation grows the cache if all reclaim priorities fail.
- Nodes are removed from MRU while referenced and reinserted on final put.
- `CACHE_MISCOMPARE_PURGE` can purge stale mismatched entries during lookup.
- Purge mode may reclaim dirty nodes; normal memory-pressure reclaim will not.
- Debug code can abort on refcount/list invariant violations when enabled.

Dependencies:
- Uses libxfs list helpers, pthread mutexes, and caller-provided cache operation callbacks.

Notable risks:
- Locking order spans hash, node, MRU, and global mutexes; misuse by callbacks can deadlock.
- `cache_report` divides by `cache->c_count` in MRU/hash summaries after only checking hit/miss activity.
