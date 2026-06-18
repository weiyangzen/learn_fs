# sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_file.h

Purpose: declares the logical block address, file abstraction hierarchy, and threaded writer interfaces for block-cache persistent files.

Important APIs/types: `LogicalBlockAddress` (`LBA`) identifies a record by cache id, file offset, and record size. `Writer` abstracts async buffer writes. `BlockCacheFile` owns common path/cache-id/block-info metadata and virtual `Append`/`Read`/`Delete`. `RandomAccessCacheFile` adds thread-safe disk reads and record parsing. `WriteableCacheFile` adds append buffering, in-memory reads while open, EOF transition, and close-to-read behavior. `ThreadedWriter` queues `IO` work items and dispatches them on worker threads.

Control flow and state: `WriteableCacheFile` tracks `buf_woff_` for the buffer being filled, `buf_doff_` for next dispatch, `pending_ios_`, `disk_woff_`, `eof_`, and `enable_direct_reads_`. Reads choose disk or buffer path based on whether EOF has occurred and buffers have been cleared. `ThreadedWriter::IO` includes a callback so the file can update pending state when a buffer write finishes.

Dependencies and integration: integrates with `CacheWriteBufferAllocator`, `LRUElement`, `PersistentCacheTier`, RocksDB file abstractions, and cache metadata via `BlockInfo`. `BlockCacheFile` inherits `LRUElement<BlockCacheFile>` so cache-file objects can be evicted by `EvictableHashTable`.

Risks and test signals: reference counts (`refs_`) are used both for lookup pinning and eviction safety; incorrect increments/decrements would block eviction or allow deletion while reading. The comment notes a write-pipeline architecture for high-throughput devices, but correctness depends on file-level serialization and buffer allocator sizing.
