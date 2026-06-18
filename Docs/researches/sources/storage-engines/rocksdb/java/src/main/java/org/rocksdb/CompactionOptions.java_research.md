# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionOptions.java

Purpose: options object for `RocksDB.compactFiles(...)`. It controls output compression, output file size limit, and per-compaction subcompaction count.

Control flow is a native-handle option wrapper with fluent setters returning `this`. `compression()` converts a native byte through `CompressionType.getCompressionType`; `setCompression()` passes the enum byte, including the special `DISABLE_COMPRESSION_OPTION` behavior documented for deferring to column-family settings. `outputFileSizeLimit()` and `maxSubcompactions()` are direct native getters. State is native configuration consumed by a compact-files call rather than Java-persisted state. Dependencies include `RocksObject`, `CompressionType`, `RocksDB`, `ColumnFamilyOptions`, `ColumnFamilyHandle`, `CompactionJobInfo`, and `DBOptions`.

Risks: compression enum drift breaks native mapping, subcompaction values override DB-level settings only when positive, and disposal before the compaction call completes would invalidate the native pointer. Tests should round-trip every field, validate special compression selection, and cover compact-files calls with output file-size and subcompaction overrides.
