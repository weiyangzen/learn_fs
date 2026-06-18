# sources/storage-engines/pebble/objstorage/objstorageprovider/sharedcache/shared_cache.go

Purpose: This file implements a local filesystem-backed cache for remote/shared object reads. It caches fixed-size blocks from remote objects, shards the cache to reduce lock contention, and asynchronously writes cache fills after remote misses.

Important types and APIs: `Cache` owns shards, write workers, block math, sharding size, logger, and metrics. `Metrics` exposes counters and Prometheus histograms. `Open`, `Close`, `Metrics`, and `ReadAt` are the public APIs. Internal `shard`, `cacheBlockState`, `whereMap`, `logicalBlockID`, `blockMath`, and `writeWorkers` implement placement, LRU, locking, and async write-back.

Control flow: `ReadAt` first attempts a prefix read from cache with `get`. Full hits return immediately; partial/no hits read the remaining range from the remote object. For writeable reads, the miss range is block-aligned and rounded up, capped at EOF, copied back to the caller, and queued to workers for cache insertion. Read-only reads, used for compaction, bypass cache population. Shards are selected by hashing file number and sharding-block index. A shard get takes read locks, moves blocks to LRU front, and reads from the cache file. A shard set skips existing blocks, uses free blocks or evicts an unlocked LRU tail block, writes to the cache file, and releases the write lock.

State and persistence: Cache data is stored in `SHARED-CACHE-###` files, but the metadata mapping is in memory and intentionally not persistent; restart overwrites/reuses cache files from scratch. Metrics are atomic in-memory counters/histograms.

Dependencies and integration: `remote_readable.go` uses `Cache.ReadAt` for remote objects. The cache depends on `vfs`, `remote.ObjectReader`, `base.DiskFileNum`, and Prometheus histograms.

Risks and test signals: Risks include races around write locks/read locks, stale zeroed blocks from unaligned writes, queue blocking, no eviction candidate when all blocks are locked, non-persistent metadata after restart, and high memory allocation for adjusted miss buffers. Tests include data-driven cache behavior, randomized concurrent reads, and internal LRU/free-list checks.
