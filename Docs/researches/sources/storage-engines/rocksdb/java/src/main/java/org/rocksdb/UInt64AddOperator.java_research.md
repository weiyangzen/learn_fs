# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/UInt64AddOperator.java

## Purpose
`UInt64AddOperator` is a Java wrapper for RocksDB's unsigned 64-bit additive merge operator. It lets users configure merge semantics that accumulate integer values.

## Important APIs and Types
The only public API is the constructor, which calls `newSharedUInt64AddOperator()` and passes the native handle to `MergeOperator`. Disposal delegates to `disposeInternalJni`.

## Control Flow, State, and Persistence
All merge behavior is native. The Java object owns a native shared merge operator handle and releases it on disposal. Persistent effects occur when configured on DB/column family options and used by merge writes.

## Dependencies and Integration Points
Depends on `MergeOperator` and JNI. It integrates with `Options`/`ColumnFamilyOptions` merge operator configuration and write paths such as `WriteBatch.merge` and `Transaction.merge`.

## Risks and Test Signals
Risks include native handle lifetime and correct encoding of unsigned 64-bit values by callers. `AbstractTransactionTest` exercises merge behavior through other configured string append operators, not this specific operator.
