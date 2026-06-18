# sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier.h

Purpose: declares `BlockCacheTier`, the disk-backed `PersistentCacheTier` implementation, including its write pipeline queue, file writer, metadata manager, cache size accounting, and statistics.

Important APIs/types: public overrides include `Insert`, `Lookup`, `Open`, `Close`, `Erase`, `Reserve`, `IsCompressed`, `GetPrintableOptions`, `Stats`, and `TEST_Flush`. Private `InsertOp` carries queued key/value writes and a quit signal; `Statistics` stores histograms and atomic counters for pipelined bytes, written/read bytes, hit/miss/error counts, dropped inserts, and latencies.

Control flow and state: construction wires a bounded insert queue, a fixed write-buffer allocator sized from config, and a `ThreadedWriter`. `TEST_Flush()` waits for the insert queue to drain but does not explicitly wait for all file IO callbacks beyond the normal writer/file path. `lock_` protects metadata, active file replacement, and capacity reservation while file-level locks protect per-file buffers and readers.

Dependencies and integration: includes RocksDB cache/persistent-cache interfaces, histograms, mutex utilities, file and metadata headers, and `BoundedQueue`. It is the concrete tier used by `NewPersistentCache()` and by tiered RAM+block configurations.

Risks and test signals: raw pointer ownership is split between `cache_file_` and metadata, so close/evict paths must remain consistent. The class assumes config validation prevents buffer/file-size deadlocks. Pipelined queue overflow silently drops `InsertOp`s at `BoundedQueue` level, only later visible through miss behavior or dropped stats.
