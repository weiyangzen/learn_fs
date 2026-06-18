# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WalFilter.java

## Purpose
`WalFilter` is a Java callback interface allowing applications to inspect or alter WAL replay during recovery.

## Important APIs and Types
`columnFamilyLogNumberMap` receives column-family id/log-number and name/id mappings. `logRecordFound` receives the current log number, file name, original `WriteBatch`, and mutable `newBatch`, returning `LogRecordFoundResult`. `name()` returns a diagnostic filter name. `LogRecordFoundResult` carries a `WalProcessingOption` and a `batchChanged` flag, with `CONTINUE_UNCHANGED` as a shared default.

## Control Flow, State, and Persistence
Native recovery calls into Java for mappings and each log record. The callback can continue, ignore a record, stop replay, mark corruption, or populate a replacement batch. If `batchChanged` is false, `newBatch` is ignored. The replacement batch must not contain more records than the original, or recovery fails.

## Dependencies and Integration Points
Depends on `Map`, `WriteBatch`, and `WalProcessingOption`. It integrates with RocksDB recovery and JNI callback plumbing.

## Risks and Test Signals
WAL filters are high-risk because incorrect return options or oversized replacement batches can discard logs or fail recovery. Callback exceptions and Java/native lifetime of batches are also sensitive. No direct WAL filter tests are included in this subset.
