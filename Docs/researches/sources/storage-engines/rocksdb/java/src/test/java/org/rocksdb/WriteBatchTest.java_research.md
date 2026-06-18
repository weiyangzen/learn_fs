# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/WriteBatchTest.java

## Purpose

This suite mirrors RocksDB C++ write-batch tests for Java. It validates batch operation recording, direct-buffer overloads, internal sequence helpers, append behavior, log/blob data, save points, range deletes, serialization, content flags, WAL termination points, and native access helpers.

## Important APIs and types

The file uses `WriteBatch`, `WriteOptions`, `RocksDB`, `CapturingWriteBatchHandler`, `WriteBatchGetter`, `ByteBuffer`, `WriteBatch.SavePoint`, and package-private `WriteBatchTestInternalHelper` native methods for sequence and append. It also calls a private native `getContents(long)`.

## Control flow

Tests construct batches, apply puts/deletes/merges/single deletes/delete ranges/log data, and either iterate with a capturing handler or inspect native debug contents. Save-point tests set nested points, roll back or pop, and assert resulting events. Serialization tests construct a second batch from `data()`. Flag tests assert `hasPut`, `hasDelete`, `hasSingleDelete`, `hasDeleteRange`, and transaction-related flags. A DB-backed test writes a delete-range batch and verifies persisted key visibility.

## State and persistence behavior

Most state is in-memory batch serialization and native sequence metadata. `deleteRange` persists the batch into a temporary DB. WAL termination point stores batch size/count/content flags at a marked boundary.

## Dependencies and integration points

This suite is a deep JNI contract for write-batch mutation APIs, callback iteration, direct-buffer marshalling, native `WriteBatchInternal`, and DB write application.

## Risks and test signals

Risks include ordering differences in native debug contents, broken save-point stack handling, oversized batch checks, direct-buffer position mistakes, serialization incompatibility, and content-flag drift. Signals are exact event lists, expected exceptions for missing save points/max bytes, data-size constants, and DB readback after range delete.
