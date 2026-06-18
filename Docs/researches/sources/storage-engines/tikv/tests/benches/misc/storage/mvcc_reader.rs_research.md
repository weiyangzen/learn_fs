# sources/storage-engines/tikv/tests/benches/misc/storage/mvcc_reader.rs

Purpose: measures `SnapshotReader::get_txn_commit_record` with short and long version chains.

Important APIs and functions: `prepare_mvcc_data` repeatedly prewrites and commits the same key for timestamps `1..=n`, then compacts RocksDB CFs. `bench_get_txn_commit_record` constructs a `SnapshotReader` for each iteration and calls `get_txn_commit_record(&key).unwrap().unwrap_single_record()`. Public bench entries cover `n=100` and `n=5`.

Control flow: setup writes MVCC history once; each iteration creates a snapshot reader over a fresh engine snapshot and resolves the transaction commit record.

State and persistence: durable test RocksDB state contains many versions for one logical key across write/default/lock CFs.

Dependencies and integration: uses API v1 test storage, `RocksEngine`, `SnapshotReader`, table row key encoding, and `txn_types::Mutation`.

Risks and test signals: repeatedly opening snapshots inside the benchmark is part of the measured cost. Signal is MVCC commit-record lookup behavior as version depth grows.
