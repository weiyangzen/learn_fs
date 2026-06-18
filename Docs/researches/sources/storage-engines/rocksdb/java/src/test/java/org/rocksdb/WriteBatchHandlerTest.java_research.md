# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/WriteBatchHandlerTest.java

## Purpose

This file verifies that Java write-batch iteration dispatches events to a handler in the same order and shape as the original batch operations.

## Important APIs and types

It uses `WriteBatch`, `CapturingWriteBatchHandler`, `CapturingWriteBatchHandler.Event`, and handler actions `PUT`, `MERGE`, `DELETE`, and `LOG`.

## Control flow

The test builds an expected event list, applies matching operations to a `WriteBatch`, iterates the batch with `CapturingWriteBatchHandler`, and compares captured events to expected events.

## State and persistence behavior

The state is serialized in-memory write-batch content. No DB write or persisted files are involved.

## Dependencies and integration points

This tests the JNI bridge from native `WriteBatch::Iterate` callbacks into a Java handler.

## Risks and test signals

Risks include callback ordering drift, log-data handling mistakes, and key/value byte copying errors. Signals are event-list size and full event equality.
