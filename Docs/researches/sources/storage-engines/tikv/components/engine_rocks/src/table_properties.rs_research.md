<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/table_properties.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/table_properties.rs

## Purpose
`table_properties.rs` adapts RocksDB table-property collections and user-collected properties to `engine_traits` abstractions. It exposes approximate range size/key counts and MVCC properties decoded from SST user properties.

## Important APIs, Types, and Functions
`UserCollectedProperties` is a transparent wrapper around `rocksdb::UserCollectedProperties` implementing `engine_traits::UserCollectedProperties`. It exposes raw `get`, `approximate_size_and_keys`, and `get_mvcc_properties`.

`TableProperties` wraps `rocksdb::TableProperties` and exposes user-collected properties plus entry count. `TablePropertiesCollection` wraps RocksDB's collection and implements iteration. `RocksEngine::get_properties_of_tables_in_range` and `get_range_properties_cf` are the raw RocksDB range-property entry points. `TablePropertiesExt::table_properties_collection` returns the wrapped collection.

## Control Flow
`table_properties_collection` delegates to `get_properties_of_tables_in_range`. That resolves the CF handle, converts each `engine_traits::Range` to a RocksDB range, calls RocksDB, and maps errors. Iteration transmutes RocksDB property references into wrapper references and stops when the callback returns false.

## State and Persistence Behavior
The module reads SST table metadata only. It does not mutate the DB, but the returned properties reflect persisted SST metadata created by table property collectors.

## Dependencies and Integration Points
It depends on `RangeProperties::decode`, `RocksMvccProperties::decode`, `util::range_to_rocks_range`, and RocksDB table properties APIs. Range split estimation, MVCC statistics, TTL scans, and administrative tooling depend on these decoded properties.

## Risks and Edge Cases
The wrappers use `repr(transparent)` and `unsafe transmute`, so correctness depends on exact wrapper layout and reference lifetimes. Missing or malformed user-collected properties return `None` for approximate sizes or MVCC properties. Range conversion allocates a temporary vector.

## Test Signals
Coverage should include tables with and without range/MVCC collectors, malformed user properties, early stop in collection iteration, multi-range queries, and CF lookup errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/table_properties.rs -->
