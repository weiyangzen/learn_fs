# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/PlainTableConfig.java research

## Purpose

`PlainTableConfig` configures RocksDB's plain-table SST format for Java. Plain tables target low-latency memory or very low-latency media and support prefix hashing.

## Important APIs and types

Defaults include variable-length keys, 10 bloom bits per key, hash table ratio 0.75, index sparseness 16, no huge TLB, plain encoding, full-scan mode disabled, and store-index-in-file disabled. Fluent setters/getters cover key size, bloom bits, hash table ratio, index sparseness, huge page TLB size, `EncodingType`, full scan mode, and storing index/bloom in the file. `newTableFactoryHandle()` creates the native table factory from the stored fields.

## Control flow

Applications configure fields in Java, pass the config to `Options.setTableFormatConfig(...)`, and `Options` calls `newTableFactoryHandle()`. Native RocksDB then builds or reads plain-table SSTs according to these settings.

## State and persistence behavior

The object stores Java configuration fields. Encoding type and store-index choices can affect newly written SST files and may be persisted in file metadata. Existing files can coexist with different encoding choices according to the comments.

## Dependencies and integration points

It extends `TableFormatConfig`, depends on `EncodingType`, and integrates with `Options.setTableFormatConfig`. It interacts with prefix extractor choices, bloom filters, hash-table sizing, mmap/read behavior, and table factory creation in native RocksDB.

## Risks and test signals

Risks include invalid ratios or sizes being rejected only by native code, huge-page configuration depending on OS setup, and performance regressions from sparse or disabled indexes. Tests should cover default values, fluent setter round-trips, DB open/write/read using plain tables, fixed and variable key sizes, full-scan mode, store-index-in-file reopen behavior, and native validation failures.
