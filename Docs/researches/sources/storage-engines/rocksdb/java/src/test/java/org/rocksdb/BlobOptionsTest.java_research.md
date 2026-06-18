# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BlobOptionsTest.java

## Purpose
`BlobOptionsTest` validates blob-related option bindings and real blob file creation behavior for default and non-default column families.

## Important APIs and Types
It covers `Options`, `ColumnFamilyOptions`, `MutableColumnFamilyOptionsBuilder`, `PrepopulateBlobCache`, `CompressionType`, `FlushOptions`, `RocksDB`, `ColumnFamilyDescriptor`, and `ColumnFamilyHandle`.

## Control Flow, State, and Persistence
Helper methods build small and large keys/values and count `.sst`/`.blob` files in the temp DB folder. Option tests assert defaults, fluent setter returns, getters, and mutable option key/value serialization. `testBlobWriteAboveThreshold` enables blob files, flushes a small value and confirms no blob, then flushes a large value and confirms a blob file plus readable values. The column-family test creates CFs with and without blob options, reopens with descriptors, verifies fetched mutable options, flushes large writes, and confirms only the blob-enabled CF creates a blob file.

## Dependencies and Integration Points
Depends on RocksDB native library, JUnit, AssertJ, temp folders, collection utilities, UTF-8 encoding, and RocksDB option/flush/CF APIs.

## Risks and Test Signals
The tests validate persistent file side effects, option round-tripping, and CF-specific blob behavior. Risks include filesystem listing assumptions, flush timing, and handle cleanup for column families created without retaining returned handles in the first open phase.
