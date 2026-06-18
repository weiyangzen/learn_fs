# sources/storage-engines/tikv/components/sst_importer/src/caching/cache_map.rs

Purpose: generic keyed cache for expensive resources such as external storage pools, with lightweight time-based garbage collection.

Important APIs and types: `CacheMap<M>` wraps `Arc<CacheMapInner<M>>`. `MakeCache` abstracts construction of a cached resource; cached resources must implement `ShareOwned` to return a shareable/owned handle. `Cached<R>` tracks resource and last-used tick. `gc_loop` periodically ticks and prunes old entries. `cached_or_create` returns an existing shared resource or builds/inserts a new cached resource.

Control flow: `cached_or_create` first attempts `DashMap::get_mut`; on miss it uses entry API to avoid duplicate insertion races, increments `EXT_STORAGE_CACHE_COUNT` hit/miss metrics, constructs via `backend.make_cache`, logs insertion, stores `Cached::new`, and returns `share_owned`. `tick` increments `now` and retains entries whose `now - last_used` is below `gc_threshold`.

State and persistence behavior: process-local cache in `DashMap<String, Cached<_>>`; no persistence. GC stops automatically when the cache map is dropped because `gc_loop` holds a weak reference.

Dependencies and integration points: used by storage cache code and importer external-storage paths. Depends on `dashmap`, `tokio::time`, and importer metrics.

Risks: GC is tick-based rather than wall-clock per entry; an entry created but never hit has `last_used = 0` and can expire after enough ticks. Concurrent misses for the same key are guarded by DashMap entry insertion, but `make_cache` still runs while holding the shard entry path. `SeqCst` is conservative but not performance-free.

Test signals: `test_basic` verifies cache creation, hit reuse, and expiration behavior with a threshold of 1.
