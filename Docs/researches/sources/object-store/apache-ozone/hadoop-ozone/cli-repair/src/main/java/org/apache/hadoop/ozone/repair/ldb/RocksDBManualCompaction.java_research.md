## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/ldb/RocksDBManualCompaction.java

Purpose: offline repair command that manually compacts one RocksDB column family for any Ozone-related RocksDB database. It is intentionally generic and warns operators to stop the owning service.

Important APIs and control flow: picocli options require `--db` and `--column-family`/`--cf`. `execute` confirms generic repair execution, then prompts a second "service stopped" warning unless dry-run is enabled. It opens the DB with latest options via `ManagedRocksDB.openWithLatestOptions`, resolves the target column family with `RocksDBUtils.getColumnFamilyHandle`, and runs `compactRange` with forced bottommost-level compaction. Errors are wrapped as `IOException`; RocksDB options and handles are closed in `finally`.

State and dependencies: mutates SST layout and removes tombstones in-place; it does not change logical key/value contents. Dependencies include managed RocksDB wrappers, `RocksDBUtils`, picocli, and `RepairTool` for dry-run/confirmation output.

Risks and test signals: running while OM/SCM/DN owns the DB can corrupt operational assumptions or hurt OM snapshot diff efficiency. `TestLdbRepair` verifies tombstones disappear, SST size shrinks, command exit succeeds, and DB/table options are preserved.
