# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ImportColumnFamilyTest.java

## Purpose

Integration coverage for importing one or more exported column-family file sets into a new column family.

## Important APIs, control flow, and dependencies

The tests use `Checkpoint.exportColumnFamily`, `ExportImportFilesMetaData`, `ImportColumnFamilyOptions`, `createColumnFamilyWithImport`, `ColumnFamilyDescriptor`, and `RocksDB`. The first test exports the default CF from one DB and imports it into `new_cf` in the same DB. The second exports default CF metadata from two DBs, combines the metadata list, and imports both into a new CF in the first DB.

## State, persistence, risks, and test signals

This directly validates persisted SST metadata handoff. Exported metadata must describe files that can be linked or copied into a new CF without losing key/value data. Risks include metadata lifetime, duplicate/range overlap handling, import option defaults, and file path correctness. Signals are reads from the imported column family for all source keys.
