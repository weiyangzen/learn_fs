# sources/storage-engines/tikv/components/engine_traits/src/table_properties.rs

Purpose: Defines generic access to table properties and user-collected SST properties.

Important APIs and control flow: `UserCollectedProperties` can fetch raw indexed properties, compute approximate size/keys, and return MVCC properties. `TableProperties` associates user properties and exposes them plus entry count. `TablePropertiesCollection` iterates table properties until a callback stops. `TablePropertiesExt` retrieves a collection covering ranges in a CF.

State, persistence, and dependencies: Implementations read persisted SST table metadata. It depends on `MvccProperties`, `Range`, and `Result`.

Integration points, risks, and test signals: Used by range, MVCC, TTL, and diagnostics. Risks include backend API drift, partial table coverage for ranges, missing property collectors, property decode failures, and mismatches with implementors that expose only user-collected properties. Test signals are mostly indirect through property collector tests and approximate-range behavior.
