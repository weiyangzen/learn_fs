# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ExportImportFilesMetaData.java

Purpose: native-backed metadata describing exported column-family files for later import. It is used by export/import column-family workflows.

Control flow is minimal: package-private constructor wraps a native handle, and `disposeInternal(long)` is native. No public accessors are present in this file, so Java treats it as an opaque token passed to import APIs. State is native metadata and may reference exported files/column-family descriptors. Dependencies include `RocksObject`, `RocksDB.createColumnFamilyWithImport`, and `ImportColumnFamilyOptions`.

Risks: opaque native ownership is the key concern; disposing too early invalidates import, while not disposing leaks native metadata. Tests should cover export-to-import lifecycle, disposal, and error behavior when metadata is reused or paired with incompatible options.
