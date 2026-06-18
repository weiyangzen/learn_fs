# sources/storage-engines/rocksdb/java/rocksjni/write_batch.cc

## Purpose
This file bridges Java `WriteBatch` and `WriteBatch.Handler` to C++ `WriteBatch`, exposing batch construction, mutation, serialization, iteration, savepoints, operation presence flags, WAL termination point metadata, and disposal.

## Important APIs, Types, and Functions
Exports include constructors from reserved bytes and serialized bytes, `count0Jni`, `clear0Jni`, savepoint APIs, `setMaxBytesJni`, put/merge/delete/singleDelete/deleteRange overloads with optional column family, direct-buffer put/delete helpers, `putLogDataJni`, `iterate`, `data`, `getDataSize`, operation flag getters, WAL termination point setters/getters, disposal, and handler creation.

## Control Flow
Most mutation methods cast the `WriteBatch*`, build lambdas around the appropriate C++ method, and use `JniUtil::kv_op`, `k_op`, or direct-buffer helpers to convert Java byte arrays or buffers into `Slice`s. Status results are converted to Java `RocksDBException`s. Iteration casts the handler handle to `WriteBatchHandlerJniCallback` and calls `WriteBatch::Iterate`. Serialization copies `WriteBatch::Data()` to a Java byte array.

## State and Persistence Behavior
The file mutates the in-memory write batch sequence of operations. Batches are persisted only when written to a DB by other APIs. Savepoint and max-bytes state live inside the batch. WAL termination point state is exposed through `MarkWalTerminationPoint` and `GetWalTerminationPoint`. Disposal deletes the C++ batch.

## Dependencies and Integration Points
It depends on RocksDB write batch APIs, internal write batch headers, generated Java JNI headers, portal conversions, and `writebatchhandlerjnicallback.h`. It integrates with Java `WriteBatch`, `WriteBatch.Handler`, `WriteOptions`, `RocksDB.write`, transaction code, and WAL/log inspection.

## Risks and Edge Cases
Direct-buffer overloads accept a nullable column-family handle to mean default column family, unlike array overloads that assert non-null for column-family variants. Handler iteration depends on callback exception conversion. Serialized constructor accepts arbitrary byte arrays and trusts RocksDB parsing later. `getWalTerminationPoint` returns a Java savepoint object from native state that must match Java expectations.

## Test Signals
Tests should cover every operation type, column-family and default variants, direct-buffer variants, serialized round trip, savepoint rollback/pop errors, handler iteration callbacks, operation presence flags, data size, WAL termination point, and disposal through try-with-resources. `write_batch_test.cc` provides native helpers for deeper internal test assertions.
