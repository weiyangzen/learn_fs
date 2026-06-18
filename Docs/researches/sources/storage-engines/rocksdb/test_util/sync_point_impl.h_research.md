# sources/storage-engines/rocksdb/test_util/sync_point_impl.h

Purpose: defines the debug-only internal state container for `SyncPoint`, plus a small allocator used to avoid circular dependencies with RocksDB arenas.

Important APIs/types: `SingleAllocator` implements only `AllocateAligned()` by resizing an internal string buffer, enough for `DynamicBloom`; other allocation methods assert. `SyncPoint::Data` stores dependency maps, callbacks, markers, mutex/condition variable, cleared point trace, bloom filter, enabled flag, and callback-running count. It provides loading, callback, processing, enable/disable, trace clearing, and marker filtering methods.

State behavior: `enabled_` is atomic for cheap checks. `DisableProcessing()` wakes all waiters so threads blocked in `Process()` can exit. `point_filter_` avoids locking for points that have no dependency/callback/marker interest.

Dependencies/integration: includes `memory/concurrent_arena.h`, `port/port.h`, `util/dynamic_bloom.h`, `util/random.h`, and public sync-point declarations. It is included by implementation files rather than being a public test API.

Risks and test signals: `SingleAllocator` is intentionally single-use and incomplete; expanding bloom usage could expose its assert-only methods. Tests should stress disable during wait, callback clearing while a callback runs, and marker filtering for different thread IDs.
