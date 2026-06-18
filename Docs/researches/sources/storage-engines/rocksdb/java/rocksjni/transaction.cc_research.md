# sources/storage-engines/rocksdb/java/rocksjni/transaction.cc

## Purpose
This file is the JNI bridge for `org.rocksdb.Transaction`, exposing C++ `ROCKSDB_NAMESPACE::Transaction` behavior to Java. It translates Java native handles, byte arrays, direct byte buffers, transaction options, snapshots, savepoints, lock metadata, write batches, and transaction lifecycle calls into C++ transaction method calls.

## Important APIs, Types, and Functions
The exported JNI functions cover snapshot control (`setSnapshot`, `setSnapshotOnNextOperation`, `getSnapshot`, `clearSnapshot`), lifecycle (`prepare`, `commit`, `rollback`, `disposeInternal`), savepoints (`setSavePoint`, `rollbackToSavePoint`), reads (`get`, `getDirect`, `multiGet`, `getForUpdate`, `multiGetForUpdate`), writes (`put`, `merge`, `delete`, `singleDelete`), untracked writes, indexing toggles, log data, counters, write options, locking helpers (`undoGetForUpdate`), recovery helpers (`rebuildFromWriteBatch`, `getCommitTimeWriteBatch`), transaction naming, IDs, waiting transaction inspection, and state mapping. Helper typedefs and functions such as `FnWriteKVParts`, `txn_write_kv_parts_helper`, `FnWriteK`, and `txn_write_k_helper` centralize callback binding for fragmented key/value operations.

## Control Flow
Most functions reinterpret a Java `long` as a RocksDB pointer, build `Slice` or `PinnableSlice` wrappers from Java inputs, call the C++ transaction API, and translate `Status` or `KVException` results back to Java exceptions or return codes. Single-key array operations use `JByteArraySlice`; direct buffer paths use `JDirectBufferSlice`; fixed-output reads use `JByteArrayPinnableSlice` or `JDirectBufferPinnableSlice` and return either copied bytes or fetch result codes. Multi-get paths use `MultiGetJNIKeys`, optional column-family handle vectors, RocksDB multi-get APIs, and `MultiGetJNIValues` for result array construction. Fragmented key/value writes iterate `byte[][]`, pin each element, build `SliceParts`, call the bound transaction method, and release all JNI references afterward.

## State and Persistence Behavior
The file mutates live transaction state: snapshots, savepoints, prepare/commit/rollback state, write batch contents, lock tracking, lock timeout, transaction name, log number, indexing state, and write options. Persistence is indirect through transaction commit and WAL/write batch integration. Returned snapshot and write batch handles are borrowed C++ pointers, while `disposeInternal` deletes the transaction object owned by the Java wrapper.

## Dependencies and Integration Points
It depends on RocksDB transaction utilities, `portal.h` JNI helpers, `kv_helper.h`, `jni_multiget_helpers.h`, and `cplusplus_to_java_convert.h`. It integrates with Java `Transaction`, `ReadOptions`, `WriteOptions`, `ColumnFamilyHandle`, `Snapshot`, `TransactionNotifier`, `WriteBatch`, and nested transaction metadata types through generated JNI headers and portal constructors.

## Risks and Edge Cases
Handle casts assume Java passes valid live native handles. Fragmented writes explicitly rely on enough JNI local references; the helper throws a RocksDB exception if `EnsureLocalCapacity` fails. Multi-part key/value helpers must release all pinned arrays on every exception path. Direct buffer paths require direct buffers and valid offsets. The transaction state enum is manually mapped to byte constants, so Java and C++ enum ordering must remain synchronized. `getName` uses `NewStringUTF(name.data())`, so embedded NUL handling depends on transaction names being UTF-compatible C strings. `getWaitingTxns` and state/ID access expose live transaction internals without ownership transfer.

## Test Signals
Coverage should exercise byte-array and direct-buffer reads/writes, column-family overloads, not-found return conventions, `getForUpdate` conflict behavior, fragmented `SliceParts` writes, savepoint rollback, transaction state byte values, waiting transaction object construction, and exception paths for RocksDB `Status`. The Java transaction samples in this subset provide behavioral signals for read committed, snapshot isolation, `getForUpdate`, savepoints, rollback, and commit conflict handling.
