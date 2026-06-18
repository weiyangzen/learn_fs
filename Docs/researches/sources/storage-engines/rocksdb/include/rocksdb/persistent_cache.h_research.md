# sources/storage-engines/rocksdb/include/rocksdb/persistent_cache.h

Purpose: This header declares the legacy persistent read-cache interface for caching IO pages or blocks on persistent media. It gives RocksDB an abstract cache tier that survives process restarts and is optimized for read caching.

Important APIs and types: `PersistentCache` defines `StatsType` as `std::vector<std::map<std::string, double>>` for per-tier stats. Its virtual API includes `Insert(const Slice& key, const char* data, size_t size)`, `Lookup(const Slice& key, std::unique_ptr<char[]>* data, size_t* size)`, `IsCompressed()`, `Stats()`, `GetPrintableOptions()`, and `NewId()`. `NewPersistentCache()` constructs an implementation from `Env`, path, capacity, logger, NVM optimization flag, and output shared pointer.

Control flow: Callers insert page data under a stable key, then later look it up into an owned buffer. `IsCompressed()` tells RocksDB whether cached bytes are serialized/compressed blocks with trailers or uncompressed blocks. `NewId()` lets multiple clients allocate numeric prefixes for cache-key sharding at startup.

State and persistence behavior: Unlike in-memory block cache, implementation state is intended to live on a persistent medium under the configured path and size. The interface copies inserted data, returns lookup data through owned buffers, and exposes tier stats. The header itself does not define eviction, crash consistency, or key namespace format; implementations own those choices.

Dependencies and integration points: It depends on `Env`, `Slice`, `Statistics`, `Status`, and `Logger`. It integrates with RocksDB block/table read paths that can use persistent cache as a read cache, and with applications configuring a cache through `NewPersistentCache()`.

Risks and edge cases: Cache keys must be unique across restarts and clients; misuse can produce stale or cross-DB cache hits. `IsCompressed()` must match the stored bytes or readers can decompress/interpret blocks incorrectly. Implementations must define how they handle partial writes, corruption, eviction, and capacity pressure. The comments contain a minor typo in "tier", but the API intent is clear.

Test signals: Tests should exercise insert/lookup round trips, misses, compressed versus uncompressed mode, persistence across reopen when supported, `NewId()` uniqueness, capacity/eviction behavior in the concrete implementation, and stats/reporting content.
