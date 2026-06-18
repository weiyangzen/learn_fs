# sources/storage-engines/rocksdb/java/rocksjni/write_batch_test.cc

## Purpose
This file exposes test-only JNI helpers for Java write batch tests. It inspects internal write batch contents by applying a batch to a temporary memtable and exposes internal sequence and append helpers.

## Important APIs, Types, and Functions
Exports include `WriteBatchTest.getContents`, `WriteBatchTestInternalHelper.setSequence`, `sequence`, and `append`. It uses `WriteBatchInternal`, `MemTable`, `ColumnFamilyMemTablesDefault`, `InternalKeyComparator`, `SkipListFactory`, `WriteBufferManager`, and internal iterator APIs.

## Control Flow
`getContents` casts the batch, creates a temporary memtable configured with bytewise comparator and skip-list factory, inserts the batch with `WriteBatchInternal::InsertInto`, iterates internal keys, parses each `InternalKey`, appends a textual representation of operation type, key, value, and sequence, checks count consistency, releases the memtable, and returns the text as a Java byte array. Internal helper methods cast write batch handles and call `WriteBatchInternal` sequence and append functions.

## State and Persistence Behavior
The file does not persist data. It builds temporary in-memory memtable state for inspection. `setSequence` mutates the sequence number stored in a write batch, and `append` mutates the first batch by appending the second.

## Dependencies and Integration Points
This file depends on RocksDB internal DB headers, test harness utilities, and generated Java test JNI headers. It is intended for RocksJava tests rather than production runtime code.

## Risks and Edge Cases
Because it uses internal RocksDB APIs, it is sensitive to internal type and constructor changes. It manually formats expected strings, so test expectations depend on exact internal operation ordering and sequence display. The temporary memtable must be ref/unref balanced; the code calls `mem->Ref()` and `delete mem->Unref()`.

## Test Signals
It is itself a test signal for Java `WriteBatch`: operation formatting should cover put, merge, delete, single delete, range delete, log data, sequence numbers, count mismatches, append behavior, and sequence mutation.
