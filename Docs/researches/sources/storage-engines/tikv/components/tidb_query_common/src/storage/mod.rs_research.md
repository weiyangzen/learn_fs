# sources/storage-engines/tikv/components/tidb_query_common/src/storage/mod.rs

Purpose: defines the storage abstraction consumed by table/index scan executors and related region lookup interfaces.

Important APIs and control flow: `Storage` exposes range scan lifecycle (`begin_scan`, `scan_next_entry`), point get (`get_entry`), key-only/commit-ts flags, cacheability, and statistics collection. Convenience methods convert `OwnedKvPairEntry` to `(Vec<u8>, Vec<u8>)`. A blanket `Storage` impl for `Box<T>` forwards calls. `FindRegionResult` reports local region lookup success or nearest next region start. `RegionStorageAccessor` asynchronously finds regions and obtains local storage for index lookup. `StubAccessor` is a non-instantiating placeholder returning `None` as an optional accessor.

State and persistence behavior: the trait allows implementations to own scan cursors and statistics, but this module stores no data itself. `OwnedKvPairEntry` can carry optional commit timestamp.

Dependencies and integration: uses `kvproto` key ranges/regions, Raft state roles, `async_trait`, and range types from `range.rs`. `scanner.rs` builds on this trait for multi-range scanning.

Risks and test signals: trait methods take owned `IntervalRange`/`PointRange`, causing allocation/copy TODOs. `StubAccessor` methods are `unimplemented!`, safe only when never instantiated. Correct cacheability depends on storage implementations returning `Some(false)` for cache-safe scans.
