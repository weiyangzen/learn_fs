# sources/storage-engines/rocksdb/utilities/persistent_cache/persistent_cache_util.h

Purpose: provides `BoundedQueue<T>`, a simple synchronized queue used by persistent-cache insert and writer pipelines.

Important APIs/types: `Push(T&&)` appends unless the configured byte-size bound would be exceeded, `Pop()` waits until an item exists and returns it by move, and `Size()` returns tracked queued bytes. The item type must provide `Size()`.

Control flow and state: queue size is updated by item size on push/pop, with a mutex and condition variable around the list. Overflow silently drops the pushed item rather than returning status.

Dependencies and integration: used for `BlockCacheTier::InsertOp` and `ThreadedWriter::IO`. Depends on RocksDB mutex and condition variable wrappers.

Risks and test signals: silent overflow is intentional for cache best-effort semantics but means callers cannot directly count drops at enqueue time. `SignalAll()` is used on each push, which is simple but can wake more waiters than needed. Coverage is indirect through persistent-cache tests and benchmarks.
