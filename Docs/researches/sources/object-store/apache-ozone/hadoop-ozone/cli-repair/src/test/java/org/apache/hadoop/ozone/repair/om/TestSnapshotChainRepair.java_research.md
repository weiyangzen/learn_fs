## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/om/TestSnapshotChainRepair.java

Purpose: unit tests for `om snapshot chain` repair validation and persistence behavior.

Important APIs and control flow: tests mock `ManagedRocksDB`, `RocksDBUtils`, and `OptionsUtil` to avoid a real DB. `setupMockDB` supplies a target `SnapshotInfo`, optional predecessor snapshots, a mocked iterator over encoded snapshot rows, and the target column-family handle. The success test runs both dry-run and real modes and verifies output plus whether `RocksDB.put` is invoked. Negative tests cover global previous equal to target ID, path previous equal to target ID, and nonexistent predecessor IDs.

State and dependencies: no real DB writes; assertions verify serialized key/value bytes passed to mocked RocksDB. Depends on `SnapshotInfo` codec and `StringCodec`.

Risks and test signals: confirms major guardrails but not global/path chain acyclicity, ordering, or real RocksDB open behavior.
