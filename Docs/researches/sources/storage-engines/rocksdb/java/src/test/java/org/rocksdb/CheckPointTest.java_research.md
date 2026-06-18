# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CheckPointTest.java

## Purpose

Tests Java checkpoint binding behavior for creating physical DB snapshots and exporting a column family for later import workflows.

## Important APIs, control flow, and dependencies

The suite uses `Checkpoint.create`, `createCheckpoint`, `exportColumnFamily`, `ExportImportFilesMetaData`, `RocksDB.open`, and `Options`. The main checkpoint test writes `key`, creates `snapshot1`, writes `key2`, creates `snapshot2`, then reopens both snapshot directories to confirm snapshot isolation. `exportColumnFamily` exports metadata twice around a second write.

## State, persistence, risks, and test signals

This is persistence-heavy: checkpoint directories must contain enough SST/MANIFEST/WAL state to reopen independently. Exported metadata must reflect the column-family files at export time. Risks include invalid DB handles, invalid paths, and binding lifetime issues; negative tests cover null DB, closed DB, and illegal checkpoint paths. Signals are reopened DB reads and expected exception types.
