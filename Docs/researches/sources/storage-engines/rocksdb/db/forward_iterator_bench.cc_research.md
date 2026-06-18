# sources/storage-engines/rocksdb/db/forward_iterator_bench.cc

Standalone benchmark for tailing/forward iterator behavior under concurrent writers and readers. It compiles only with gflags and not on macOS/Windows; otherwise it provides a placeholder `main`.

Gflags configure writer/reader counts, write rate, value size, shard count, memtable size, block cache size, block size, runtime, cache-only-first behavior, and iterate upper-bound usage. `Stats` holds padded atomics. `Key` stores shard and sequence number in big-endian binary format. `ShardState` stores last-written/read counters, iterators, and optional upper-bound slice. `Reader`, `Writer`, and `StatsThread` implement the workload.

`main()` opens a DB with no compression, no compaction style, high L0 triggers, direct IO for flush/compaction, and configured table/cache settings. Writers choose assigned shards randomly, write monotonic `(shard, seqno)` keys at the configured rate, and notify readers. Readers keep tailing iterators per shard, optionally try a cache-only iterator first, seek to the next unread key, and then call `Next()` until caught up or an incomplete cache miss occurs. The stats thread prints throughput and cache misses once per second.

Persistent state is just generated DB data in a recreated test path. Benchmark state is atomics, semaphores, queues, iterators, and threads. `iterate_upper_bound` constrains each shard iterator to its shard key range.

Dependencies include RocksDB public DB APIs, block-based table options/cache creation, test path helpers, gflags compatibility, POSIX semaphores, and `port::Thread`. It indirectly exercises `ForwardIterator` when RocksDB selects tailing iterator internals.

Risks: this is not deterministic test coverage; assertions validate key order but behavior depends on runtime flags and platform. Packed binary keys and direct casts are intentionally platform constrained. Negative runtime can run indefinitely. Signals are throughput, cache-miss count, and assertion failures during concurrent write/read pressure.
