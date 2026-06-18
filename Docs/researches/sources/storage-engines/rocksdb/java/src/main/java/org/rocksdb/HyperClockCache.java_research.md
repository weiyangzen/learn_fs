# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HyperClockCache.java

Purpose: experimental `Cache` implementation wrapping RocksDB HyperClockCache, intended as a CPU-efficient block-cache alternative under high parallelism/contention.

Control flow is constructor-only JNI allocation with capacity, estimated entry charge, shard bits, and strict capacity limit; disposal forwards to native `disposeInternalJni`. State is native cache state inherited through `Cache`, used primarily by `BlockBasedTableOptions.block_cache`. Dependencies include `Cache`, `Experimental`, and block-based table options.

Risks: marked experimental; comments warn it is not a general cache, requires tuning `estimatedEntryCharge`, can dilute priorities, and can perform poorly for small/pinned caches. Changing capacity may reduce efficiency. Tests should cover construction/disposal, use as block cache in a DB, strict-capacity behavior, shard-bit settings, and performance/regression benchmarks versus LRUCache under contention.
