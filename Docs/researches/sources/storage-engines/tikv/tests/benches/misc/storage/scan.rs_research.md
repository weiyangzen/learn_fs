# sources/storage-engines/tikv/tests/benches/misc/storage/scan.rs

Purpose: ignored benchmark for scanning through MVCC tombstones, documenting and measuring the cost of deleted-but-retained MVCC keys.

Important APIs and functions: `bench_tombstone_scan` uses `KvGenerator` to create 100,000 keys, then for each key writes a put and a delete at increasing timestamps. The benchmark repeatedly scans from generated keys and expects no visible rows.

Control flow: large setup alternates prewrite/commit for put and delete mutations. Iteration performs `store.scan(..., limit=1, key_only=false, version=next_ts)` and asserts empty results.

State and persistence: MVCC tombstones remain in test storage even though logical rows are deleted.

Dependencies and integration: uses `SyncTestStorageBuilder`, `test_util::KvGenerator`, `Context`, `Mutation`, and `txn_types::Key`.

Risks and test signals: marked `#[ignore]`, so it is opt-in and expensive. Signal is scan degradation caused by tombstone density.
