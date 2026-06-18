<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/snapshot.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/snapshot.rs

## Purpose
`snapshot.rs` implements `engine_traits::Snapshot` for the RocksDB backend. `RocksSnapshot` owns an unsafe RocksDB snapshot tied to an `Arc<DB>` and exposes read-only point lookup, iteration, CF listing, and sequence-number reporting against that stable sequence.

## Important APIs, Types, and Functions
`RocksSnapshot::new(Arc<DB>)` calls `db.unsafe_snap()` and stores the returned `UnsafeSnap`. `Drop` releases it with `db.release_snap`. Trait implementations include `Snapshot`, `Iterable`, `Peekable`, `CfNamesExt`, and `SnapshotMiscExt`.

`iterator_opt` converts `engine_traits::IterOptions` to `RocksReadOptions`, installs the snapshot pointer on RocksDB read options, resolves the CF handle, and returns `RocksEngineIterator`. `get_value_opt` and `get_value_cf_opt` do the same for point lookups and wrap raw DB vectors as `RocksDbVector`.

## Control Flow
All read paths create raw RocksDB read options from trait options, set the snapshot before invoking RocksDB, then call either DB-level or CF-level operations. CF reads pass through `util::get_cf_handle`, so missing CF names become engine errors.

## State and Persistence Behavior
The snapshot pins RocksDB state until drop and can hold old versions/SSTs alive. It does not mutate stored data. `sequence_number` exposes the snapshot sequence through `UnsafeSnap`.

## Dependencies and Integration Points
It integrates `rocksdb::DB`, `DBIterator`, and `UnsafeSnap` with `engine_traits` read abstractions. It uses `options::RocksReadOptions`, `db_vector::RocksDbVector`, `util::get_cf_handle`, and `r2e` error conversion.

## Risks and Edge Cases
The type is marked `Send` and `Sync` manually, so the safety contract depends on RocksDB snapshot lifetime and `Arc<DB>` staying alive until `release_snap`. Every read option path must install the snapshot before use; missing that would turn snapshot reads into live reads. Long-lived snapshots can increase storage pressure.

## Test Signals
The `engine_tirocks` engine tests show expected snapshot behavior: data written after snapshot creation is visible to the engine but not the snapshot. Equivalent RocksDB snapshot tests should cover point reads, CF reads, scans, and release behavior under compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/snapshot.rs -->
