# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompressionType.java

Purpose: enum of RocksDB compression algorithms/options: no compression, Snappy, zlib, bzip2, LZ4, LZ4HC, Xpress, ZSTD, and disabled option.

Control flow is byte mapping through `getValue()` and `getCompressionType(byte)`, which scans values and throws on unknown bytes. State is immutable and integrated with `CompactionOptions`, `ColumnFamilyOptions`, and option-file parsing/serialization. Java does not check whether a codec is compiled into the native library.

Risks: native codec availability differs by build, unknown bytes throw, and `DISABLE_COMPRESSION_OPTION` is semantically different from `NO_COMPRESSION`. Tests should verify byte mappings, invalid-byte behavior, compact-files behavior with disabled option, and native builds with/without optional codecs.
