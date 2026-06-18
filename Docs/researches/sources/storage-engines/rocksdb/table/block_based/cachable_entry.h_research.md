## sources/storage-engines/rocksdb/table/block_based/cachable_entry.h

Purpose: declares `CachableEntry<T>`, a move-only handle for objects that may be cached, uniquely owned, or unowned. It centralizes release/delete behavior for block-like objects returned by block-based table readers.

Important APIs/types: constructors accept value pointer, cache pointer, cache handle, and ownership flag. Public methods include move construction/assignment, `IsEmpty()`, `IsCached()`, accessors, `Reset()`, `ResetEraseIfLastRef()`, `TransferTo(Cleanable*)`, `SetOwnedValue()`, `SetUnownedValue()`, `SetCachedValue()`, and `As<TWrapper>()` for layout-compatible block wrapper casts.

Control flow: destruction and reset call `ReleaseResource()`, which releases cache handles or deletes owned values. Moves transfer all management fields and clear the source. `TransferTo()` registers cache-handle release or value deletion cleanup with a `Cleanable`, then clears this entry so iterator cleanup owns the resource. Setter methods are idempotent for identical current values and otherwise reset before installing new state.

State and persistence behavior: runtime ownership state is `value_`, `cache_`, `cache_handle_`, and `own_value_`. No data is persisted. Cache release can optionally erase if this is the last reference via `ResetEraseIfLastRef()`.

Dependencies/integration points: depends on RocksDB `Cache`, `Cleanable`, likely/unlikely branch macros, and advanced cache handle APIs. Used by table reader paths that may return cached blocks, non-cached owned blocks, or pinned/unowned objects and transfer them to iterators.

Risks: invariants require cache and handle to be both null or both non-null, and cached entries cannot own values. `As<TWrapper>()` relies on identical object size and pointer-compatible wrapper layout; misuse would be unsafe. Unowned values require external lifetime management.

Test signals: no direct tests in this set, but reader and iterator tests stress cleanup through cache hits/misses, block pinning, strict capacity failures, and iterator transfer paths.
