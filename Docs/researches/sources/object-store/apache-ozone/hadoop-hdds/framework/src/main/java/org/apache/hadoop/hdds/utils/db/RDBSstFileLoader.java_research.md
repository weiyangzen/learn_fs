# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBSstFileLoader.java

## Purpose
`RDBSstFileLoader` ingests external RocksDB SST files into a target column family.

## Important APIs and Types
The package-private `load(RocksDatabase db, ColumnFamily family, File externalFile)` method skips empty files and otherwise creates `ManagedIngestExternalFileOptions`, sets `ingestBehind(false)`, and calls `db.ingestExternalFile`.

## Control Flow and State
The class is stateless. Ingest options are created and closed with try-with-resources for each load operation.

## Persistence, Dependencies, and Integration
It mutates RocksDB persistent state by ingesting SST contents. Dependencies include `RocksDatabase`, `ColumnFamily`, `ManagedIngestExternalFileOptions`, and Java `File`. It is a low-level helper for bulk-load/import paths.

## Risks and Test Signals
Skipping zero-length SSTs avoids RocksDB exceptions but may hide upstream empty-file generation. Tests should cover empty-file no-op, successful ingest path, option setting, exception propagation from RocksDB, and target column-family selection.
