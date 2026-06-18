<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/mvcc_properties.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/mvcc_properties.rs

Purpose: encodes, decodes, and queries MVCC table properties stored in RocksDB SST user properties.

Important APIs/types/functions: property-name constants, `RocksMvccProperties::{encode, decode}`, and `MvccPropertiesExt for RocksEngine::get_mvcc_properties_cf`.

Control flow: encoding writes timestamps, row/version/delete counts, stale/delete timestamp ranges, and TTL properties into `UserProperties`. Decoding reads required fields and supplies compatibility defaults for older SSTs missing delete/stale fields. Querying aggregates decoded table properties for a range, skipping tables whose minimum timestamp is newer than the safe point.

State and persistence behavior: defines the on-SST metadata format used by GC, split heuristics, and stats. It does not mutate DB data.

Dependencies/integration: used by `properties.rs` collectors and range stats; depends on `engine_traits::MvccProperties`, `txn_types::TimeStamp`, and TTL property helpers.

Risks: missing required properties abort aggregation with `None`; compatibility defaults can over-approximate old data. Safe-point filtering is table-level, not entry-level.

Test signals: collector tests in `properties.rs` validate MVCC encoding/decoding for transactional and RawKV modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/mvcc_properties.rs -->
