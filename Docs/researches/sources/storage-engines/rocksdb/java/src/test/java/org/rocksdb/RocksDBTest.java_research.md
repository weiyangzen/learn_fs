# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/RocksDBTest.java

## Purpose

This is the broad integration suite for the Java `RocksDB` JNI facade. It covers opening databases, column-family management, put/get/write/delete/merge APIs, byte-buffer and offset overloads, range deletion, compaction, background-work controls, live metadata, properties, WAL operations, tracing, mutable options, and lifecycle checks.

## Important APIs and types

The suite uses `RocksDB`, `Options`, `DBOptions`, `ColumnFamilyOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `WriteOptions`, `ReadOptions`, `WriteBatch`, `FlushOptions`, `CompactRangeOptions`, `CompactionOptions`, `MutableColumnFamilyOptions`, `MutableDBOptions`, metadata types (`LiveFileMetaData`, `ColumnFamilyMetaData`, `TableProperties`), `Range`, `Slice`, `StringAppendOperator`, and `AbstractTraceWriter`. Helper class `Segment` verifies byte-array offset/length overloads. `InMemoryTraceWriter` captures trace bytes.

## Control flow

Tests repeatedly create a temporary DB, perform a focused sequence, and assert the Java-facing outcome. Early tests cover open paths and column-family creation/reopen. Write-path tests cover byte-array, direct `ByteBuffer`, heap `ByteBuffer`, offset/length overloads, batch writes, merge operators, deletes, single deletes, range deletes, and clipped column families. Compaction tests write many records, flush, compact by range or level, and inspect level properties. Metadata tests query approximate sizes, memtable stats, live files, live file checksums, table properties, column-family metadata, sorted WAL files, and suggested compaction ranges. Lifecycle tests destroy databases, cancel/pause background work, enable file deletion, set mutable options, start/end traces, and check `isClosed()`.

## State and persistence behavior

The file exercises both in-memory memtable state and durable state after flush/compaction/reopen. WAL operations are tested through flush/sync and sorted log file queries. External file and manifest-visible state is inspected through live-file and metadata APIs. Temporary folders isolate filesystem persistence, while try-with-resources closes native handles in the required order.

## Dependencies and integration points

This suite is a high-value JNI integration point between Java wrappers and core RocksDB C++ behavior: locking, column families, compaction, properties, table metadata, file checksums, trace writing, mutable option marshaling, and `ByteBuffer` position/limit semantics.

## Risks and test signals

Risks include native handle leaks, wrong `ByteBuffer` position mutation, incorrect offset overload slicing, unstable compaction assumptions, DB lock behavior changes, and metadata shape drift. Signals include exact byte equality, exception code/subcode checks, level/file property assertions, successful no-op lifecycle calls, and non-empty trace data.
