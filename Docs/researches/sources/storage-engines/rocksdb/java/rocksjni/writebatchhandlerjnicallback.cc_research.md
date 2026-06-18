# sources/storage-engines/rocksdb/java/rocksjni/writebatchhandlerjnicallback.cc

## Purpose
This file implements the C++ `WriteBatchHandlerJniCallback` that lets a Java `WriteBatch.Handler` receive callbacks while RocksDB iterates a native write batch.

## Important APIs, Types, and Functions
The constructor caches Java method IDs for put, merge, delete, single delete, delete range, log data, blob index, prepare/commit/rollback/noop markers, commit-with-timestamp, and continue. It implements `WriteBatch::Handler` methods such as `PutCF`, `Put`, `MergeCF`, `DeleteCF`, `SingleDeleteCF`, `DeleteRangeCF`, `LogData`, `PutBlobIndexCF`, `MarkBeginPrepare`, `MarkEndPrepare`, `MarkNoop`, `MarkRollback`, `MarkCommit`, `MarkCommitWithTimestamp`, and `Continue`. Helper methods `kv_op` and `k_op` convert native slices to Java byte arrays and convert Java `RocksDBException` back to C++ `Status`.

## Control Flow
For key/value callbacks, the handler copies slices into Java byte arrays, calls the matching Java method, deletes local refs, and returns OK or a status extracted from a thrown `RocksDBException`. Key-only callbacks follow the same pattern with one byte array. Marker methods either call Java directly or use `k_op`/`kv_op` for transaction IDs and timestamps. `Continue` calls the Java continue method and returns whether iteration should proceed.

## State and Persistence Behavior
The callback stores cached method IDs and a `JNIEnv*` captured at construction. It does not mutate persistence directly; it observes batch contents during iteration. Java callbacks may throw RocksDB exceptions that influence native iteration status.

## Dependencies and Integration Points
It depends on `writebatchhandlerjnicallback.h` and `portal.h`. It is created by `write_batch.cc` and passed into `WriteBatch::Iterate`, integrating with Java `WriteBatch.Handler`.

## Risks and Edge Cases
The file stores `m_env` rather than attaching per callback, so it assumes iteration occurs on the same Java-attached thread used to create the handler. Unexpected Java exceptions that are not convertible to RocksDB `Status` are described and often result in OK for status-returning callbacks, as marked by TODO comments. Frequent slice copying can be expensive for large batches. Constructor method lookup failures leave partially initialized callback objects.

## Test Signals
Tests should verify every callback type, column-family IDs, transaction marker callbacks, Java `continue` stopping iteration, Java `RocksDBException` conversion to native `Status`, behavior for unexpected exceptions, and local reference cleanup on large batches.
