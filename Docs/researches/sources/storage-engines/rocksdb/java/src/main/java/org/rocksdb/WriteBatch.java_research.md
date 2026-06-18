# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteBatch.java

## Purpose
`WriteBatch` is the Java wrapper for an atomic ordered collection of RocksDB updates. It extends `AbstractWriteBatch` and adds serialization, iteration, WAL termination, operation flags, and callback support.

## Important APIs and Types
Constructors create empty, reserved-size, serialized, or native-backed batches. Public methods include `iterate(Handler)`, `data()`, `getDataSize()`, `hasPut/hasDelete/hasSingleDelete/hasDeleteRange/hasMerge/hasBeginPrepare/hasEndPrepare/hasCommit/hasRollback`, `markWalTerminationPoint()`, and `getWalTerminationPoint()`. `Handler` is a JNI callback object with abstract callbacks for puts, merges, deletes, range deletes, log data, blob indexes, and 2PC markers. `SavePoint` records batch size, count, and content flags.

## Control Flow, State, and Persistence
Mutation methods required by `AbstractWriteBatch` delegate to native put/merge/delete/single-delete/delete-range/log/savepoint functions. Native state stores ordered operations and serialized bytes. The constructor from native handle may disown the handle when C++ manages lifetime; `BatchResult` uses the owning variant. `data()` returns serialized state that can reconstruct another `WriteBatch`.

## Dependencies and Integration Points
Depends on `AbstractWriteBatch`, `RocksCallbackObject`, `ColumnFamilyHandle`, `ByteBuffer`, and JNI. It integrates with `RocksDB.write`, transactions, WAL iteration, backups, and `WriteBatchWithIndex.getWriteBatch`.

## Risks and Test Signals
Thread safety is limited: const methods can be concurrent, mutations require external synchronization. Native handle ownership differs by constructor. Single-delete semantics are constrained by RocksDB rules. `AbstractTransactionTest.rebuildFromWriteBatch` and `getCommitTimeWriteBatch` exercise transaction integration, while backup and ByteBuffer tests use write batches indirectly and directly.
