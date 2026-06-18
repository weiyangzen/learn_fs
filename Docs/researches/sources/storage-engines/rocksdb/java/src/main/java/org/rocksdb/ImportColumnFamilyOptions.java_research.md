# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ImportColumnFamilyOptions.java

Purpose: native options for `RocksDB.createColumnFamilyWithImport(...)`. The exposed option controls whether imported files are moved into place or copied/linked according to native behavior.

Control flow allocates a native options object, exposes `moveFiles()` and fluent `setMoveFiles(boolean)`, and relies on inherited `RocksObject` disposal. State is native import configuration consumed with `ColumnFamilyDescriptor` and `ExportImportFilesMetaData`. Dependencies include `RocksDB`, `ColumnFamilyDescriptor`, and export/import metadata.

Risks: moving files has destructive/lifetime implications for exported file locations; Java does not expose additional import validation; disposal timing matters around import calls. Tests should round-trip `moveFiles`, import a column family with move enabled/disabled, verify source file handling, and cover error behavior for missing or incompatible metadata.
