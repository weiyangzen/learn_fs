# sources/storage-engines/tikv/components/hybrid_engine/src/observer/write_batch.rs

Purpose: write-batch observer that mirrors data-CF raftstore writes into the region cache.

Important APIs/types/functions: `RegionCacheWriteBatchObserver`, `HybridObservableWriteBatch`, `ObservableWriteBatch`, `WriteBatch`, and `Mutable` impls.

Control flow: observer creates a cache write batch. Region preparation and mutations are forwarded. `write_opt_seq` sets sequence number then writes cache batch; `post_write` compacts lock CF. `put_cf` only mirrors data CFs, while range deletes are forwarded as cache eviction signals.

State and persistence: disk write is handled by wrapper; this observer mutates in-memory cache state using aligned sequence numbers.

Dependencies/integration: raftstore coprocessor observable write batches, `engine_traits`, and `in_memory_engine::RegionCacheWriteBatch`.

Risks: unimplemented direct write methods panic if used outside expected boxed observable path; unwraps in `write_opt_seq` turn cache write errors into panics.

Test signals: covered by write-batch integration tests.
