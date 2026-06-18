# sources/storage-engines/tikv/components/engine_tirocks/src/properties/table.rs

Purpose: Adapts TiRocks table-property collections and user-collected property maps to the engine-trait property abstraction.

Important APIs and control flow: `RocksUserCollectedProperties` is a transparent wrapper over TiRocks `UserCollectedProperties`; `get` returns raw property values and `approximate_size_and_keys` decodes `RangeProperties` to compute range distance. `RocksTablePropertiesCollection` wraps `OwnedTablePropertiesCollection` and iterates user-collected properties until the callback returns false. `RocksEngine::properties_of_tables_in_range` resolves the CF handle, calls TiRocks `properties_of_tables_in_range`, and returns the owned collection.

State, persistence, and dependencies: The state being read is persisted per-SST table metadata, not live memtable data. It depends on TiRocks builtin table property collections and the local range property decoder.

Integration points, risks, and test signals: This is the shared utility used by range, TTL, MVCC, and table property queries. Risks include the `unsafe` transparent transmute, extra allocation of range tuples, missing CF errors, and API drift: this file's implementation surface uses a user-collected-properties collection shape while the adjacent `engine_traits/src/table_properties.rs` in this snapshot declares a `TableProperties`-oriented collection. Tests are indirect through range/TTL/MVCC property callers.
