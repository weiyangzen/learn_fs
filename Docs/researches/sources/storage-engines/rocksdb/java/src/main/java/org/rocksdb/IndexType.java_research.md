# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/IndexType.java research

## Purpose

`IndexType` maps Java block-based table index choices to RocksDB's native table factory. It lets Java applications choose between compact binary-search indexes, prefix hash indexes, two-level indexes, and binary indexes that include each data block's first key.

## Important APIs and types

The enum values are `kBinarySearch`, `kHashSearch`, `kTwoLevelIndexSearch`, and `kBinarySearchWithFirstKey`. `getValue()` is public and returns the byte passed to JNI. The comments document important prerequisites and costs, such as prefix extractor dependence for hash search and larger indexes for first-key indexes.

## Control flow

The enum itself has no logic beyond constant construction. Configuration classes read `getValue()` and pass the byte to native table factory creation, where RocksDB chooses the concrete index implementation.

## State and persistence behavior

Only immutable byte constants are stored in Java. The chosen index type affects newly built SST files and table readers; for persisted SSTs, index layout is part of the file format produced by native RocksDB.

## Dependencies and integration points

It integrates with `BlockBasedTableConfig`, prefix extractors, comparators, and `IndexShorteningMode`. Java must preserve parity with native C++ enum ordering and values.

## Risks and test signals

The sharp edge is that `kHashSearch` depends on a prefix extractor and `kBinarySearchWithFirstKey` can substantially increase index size. Tests should cover option creation, native option round-trips, opening DBs with each mode, prefix lookup behavior for hash indexes, and iterator block-read counters for first-key indexes.
