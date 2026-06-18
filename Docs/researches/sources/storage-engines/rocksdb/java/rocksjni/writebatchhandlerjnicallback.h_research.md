# sources/storage-engines/rocksdb/java/rocksjni/writebatchhandlerjnicallback.h

## Purpose
This header declares the JNI adapter that implements RocksDB `WriteBatch::Handler` by dispatching each write batch record to Java.

## Important APIs, Types, and Functions
`WriteBatchHandlerJniCallback` inherits from `JniCallback` and `WriteBatch::Handler`. It declares overrides for write operations, range deletes, blob index records, transaction prepare/commit/rollback markers, `Continue`, and private helpers `kv_op` and `k_op`. Private state includes `JNIEnv* m_env` and cached `jmethodID`s for all Java callbacks.

## Control Flow
The class contract is callback driven: RocksDB iteration invokes handler methods, the implementation converts `Slice` data into Java arrays, calls Java methods, and maps Java exceptions to C++ statuses where the RocksDB handler API supports status returns.

## State and Persistence Behavior
The class stores callback identity and method IDs only. It does not own write batch data and does not persist data. It can influence iteration status through returned `Status` and `Continue`.

## Dependencies and Integration Points
It includes RocksDB `write_batch.h` and RocksJNI `jnicallback.h`. It is used by `write_batch.cc` and the Java `WriteBatch.Handler` API.

## Risks and Edge Cases
Because the header includes `JNIEnv*` as object state, thread-affinity assumptions are part of the design. API drift in RocksDB `WriteBatch::Handler` would require header updates. Exception conversion behavior depends on portal helpers.

## Test Signals
Compile-time checks should catch missing handler overrides. Runtime tests should cover callback dispatch for every declared method, stopping iteration, exception-to-status conversion, and handler disposal.
