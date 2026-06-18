# File Research: sources/virtualization/spdk/lib/ftl/ftl_nv_cache.c

Implements the non-volatile cache lifecycle, write path, compaction path, recovery helpers, chunk state persistence, scrubbing, throttling, and JSON property reporting.

Major behaviors:
- Initialization allocates chunk objects, metadata pools, P2L map pools, chunk metadata pools, free-state persistence pools, and compactor objects.
- Chunks move through `FREE`, `OPEN`, `CLOSED`, and `INACTIVE`; lists and counters track free/open/full/compacting/inactive/free-persist chunks.
- User writes reserve sequential space in the current/open chunk, pin L2P, submit through the NV-cache device type, update L2P to cache addresses, and advance/close chunks.
- Closing a chunk writes tail P2L metadata, computes its CRC, persists chunk metadata as `CLOSED`, then moves it to the full list.
- Compaction reads valid cache blocks, pins LBAs, verifies current L2P still points to cache addresses, queues valid data to the base writer, then frees compacted chunks.
- Recovery restores chunk states, walks tail metadata, recovers open chunks through the cache-device implementation, persists recovered P2L maps, and closes recovered chunks.
- Shutdown/upgrade paths halt opening, close the current chunk by skipping unwritten blocks, persist free-state transitions, and optionally keep compaction running for upgrade preparation.

Notable risk/behavior: most IO failure handling aborts unless `SPDK_FTL_RETRY_ON_ERROR` is enabled. Resource sizing is tightly coupled to `FTL_MAX_OPEN_CHUNKS`, `FTL_MAX_COMPACTED_CHUNKS`, and `FTL_NV_CACHE_NUM_COMPACTORS`.
