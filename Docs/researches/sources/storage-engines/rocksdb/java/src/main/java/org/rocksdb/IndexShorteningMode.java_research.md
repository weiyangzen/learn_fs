# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/IndexShorteningMode.java research

## Purpose

`IndexShorteningMode` exposes the RocksDB choice for how much block index separator keys may be shortened. It trades index size against iterator seek precision, especially for direct-IO or no-cache workloads where an over-shortened separator can force unnecessary data block reads.

## Important APIs and types

The enum values are `kNoShortening`, `kShortenSeparators`, and `kShortenSeparatorsAndSuccessor`. Each stores a native byte, returned by package-private `getValue()`. The detailed class comment is the most important API documentation: it explains separator placement between blocks and the special cost of shortening the final file upper-bound key.

## Control flow

There is no active Java control flow. Configuration code serializes the chosen constant to a byte; native table-building code decides how to encode index keys when writing new tables.

## State and persistence behavior

The Java state is immutable enum metadata. The selected value affects newly written SST index entries and can therefore become part of persistent table-file layout. Existing SST files are not rewritten by changing the Java option.

## Dependencies and integration points

This enum is used with block-based table configuration and is related to `IndexType.kBinarySearchWithFirstKey`, direct reads, and iterator seek behavior. Correctness depends on native RocksDB interpreting the byte values identically.

## Risks and test signals

Byte-value drift would change SST index encoding policy. Behavioral tests should build tables under each mode and verify table-option round-trips, iterator seek correctness, and performance-sensitive signals such as unnecessary block reads under `PerfContext`.
