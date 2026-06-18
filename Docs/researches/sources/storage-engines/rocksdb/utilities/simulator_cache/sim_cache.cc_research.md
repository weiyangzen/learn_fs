# sources/storage-engines/rocksdb/utilities/simulator_cache/sim_cache.cc

Purpose: implements `SimCache`, a wrapper cache that forwards real cache operations to a target cache while maintaining a separate key-only simulated cache and optional activity log.

Important APIs and control flow: internal `CacheActivityLogger` starts/stops bounded logging, writes `LOOKUP` and `ADD` lines, tracks background status, and auto-stops on max size or error. `SimCacheImpl::Insert()` inserts key-only metadata into the simulated cache if absent, logs the add, then forwards the real insert to `target_` if present. `Lookup()` and `StartAsyncLookup()` call `HandleLookup()` to update simulated hit/miss counters/tickers and log lookups before forwarding. Capacity, strict limit, usage, pinned usage, erase, value, id, helper, and iteration APIs delegate to the target cache while sim-capacity/usage APIs address the key-only cache.

State and persistence: state includes `key_only_cache_`, atomic hit/miss counters, optional target stats pointer use, and activity log file writer. The activity log is persistent on disk until caller removes it; cache contents are normal cache memory state.

Dependencies and integration: uses RocksDB cache API, LRU cache factory, statistics tickers, writable file writer, Env/FileSystem, mutexes, and public `rocksdb/utilities/sim_cache.h`. `NewSimCache()` builds the key-only LRU cache with metadata charge disabled.

Risks and test signals: `stats_` member is initialized null and reset_counter sets ticker counts through it; per-lookup stats are recorded from the lookup call instead. Several methods assume `target_` is non-null, while `Insert/Lookup` tolerate null; construction from public factory normally supplies target. `num_shard_bits >= 20` returns null. Tests validate counters, strict capacity interaction, simulated usage, and activity logging size bounds.
