# sources/storage-engines/tikv/components/engine_traits/src/mvcc_properties.rs

Purpose: Defines MVCC statistics collected from table properties and the trait for querying them.

Important APIs and control flow: `MvccProperties` tracks timestamp bounds, row/version/put/delete counts, max row versions, TTL properties, and timestamp spans for discardable stale versions and deletes. `new` initializes extrema, and `add` merges another property set. `MvccPropertiesExt::get_mvcc_properties_cf` returns optional MVCC properties for a CF, safe point, and key range.

State, persistence, and dependencies: Implementations usually decode persisted SST user properties and may estimate discardable versions from timestamps. Dependencies include `txn_types::TimeStamp` and `TtlProperties`.

Integration points, risks, and test signals: Used by GC, compaction, region stats, and range-key fallback in TiRocks. Risks include uniform-distribution assumptions, timestamp extrema defaults, delete/stale version estimation error, and TTL merge semantics. Tests are in implementor property collectors and range fallback tests.
