# sources/storage-engines/tikv/tests/benches/misc/storage/incremental_get.rs

Purpose: compares regular MVCC point reads through `SnapshotStore::get` with `SnapshotStore::incremental_get_entry` for table lookup patterns.

Important APIs and functions: `table_lookup_gen_data` builds a `SyncTestStorage`, prewrites and commits 30,000 row keys, compacts `write`, `default`, and `lock` CFs, opens a `SnapshotStore<Arc<RocksSnapshot>>`, and returns every 30th key. `bench_table_lookup_mvcc_get` loops over keys with a fresh `Statistics`; `bench_table_lookup_mvcc_incremental_get` loops over the same key set using incremental get.

Control flow: data setup is outside `Bencher::iter`; benchmark iterations scan a stable ordered key list. The incremental benchmark keeps a mutable `SnapshotStore` across iterations to exercise cursor reuse.

State and persistence: test storage writes MVCC data into RocksDB CFs, then compacts them to reduce setup artifacts. The snapshot is read-only during benchmarking.

Dependencies and integration: uses `test_storage::SyncTestStorageBuilder`, `tidb_query_datatype::codec::table`, `tikv::storage::{Engine, SnapshotStore, Store}`, and `txn_types::{Key, Mutation}`.

Risks and test signals: snapshot timestamp `10` and committed data at ts `2` model visible historical reads. Cursor state can bias results if key order changes. Signal is relative performance of incremental lookup optimization on table rows.
