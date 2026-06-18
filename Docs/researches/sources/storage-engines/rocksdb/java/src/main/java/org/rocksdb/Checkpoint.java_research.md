# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Checkpoint.java

- **Purpose:** Java wrapper for RocksDB checkpoint and column-family export functionality.
- **Important APIs/types/functions:** Static `create(RocksDB db)` validates a non-null initialized DB. Instance methods are `createCheckpoint(String checkpointPath)` and `exportColumnFamily(ColumnFamilyHandle, String)`. Native hooks create/dispose checkpoint objects and write checkpoint/export data.
- **Control flow:** `create` performs Java validation before constructing a native checkpoint handle from the DB handle. `createCheckpoint` delegates to native checkpoint creation. `exportColumnFamily` passes checkpoint and column-family handles and wraps the returned metadata handle in `ExportImportFilesMetaData`.
- **State and persistence behavior:** Native checkpoint creation persists an openable snapshot directory using hard links/copies. Export persists files/metadata for a column family. Java state is only the checkpoint native handle.
- **Dependencies:** Depends on `RocksDB`, `ColumnFamilyHandle`, `ExportImportFilesMetaData`, `RocksObject`, and `RocksDBException`.
- **Integration points:** Used for backups/snapshots, cloning, export/import workflows, and tests needing filesystem snapshots of live DBs.
- **Risks:** Checkpoint path/export path filesystem errors surface from native code. The DB and column-family handles must remain valid. Hard-link behavior assumes same-disk support for efficient checkpoints.
- **Test signals:** Null/closed DB validation, checkpoint directory contents and reopenability, column-family export/import metadata, invalid paths, and disposal.
