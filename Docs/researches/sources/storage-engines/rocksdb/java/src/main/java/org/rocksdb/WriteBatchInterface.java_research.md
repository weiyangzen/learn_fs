# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteBatchInterface.java

## Purpose
`WriteBatchInterface` defines the common mutation contract for `WriteBatch`, `WriteBatchWithIndex`, and transaction-like batch wrappers.

## Important APIs and Types
The interface covers `count`, byte-array and `ByteBuffer` `put`, column-family variants, `merge`, `delete`, experimental `singleDelete`, `deleteRange`, `putLogData`, `clear`, savepoint operations, `setMaxBytes`, and `getWriteBatch`.

## Control Flow, State, and Persistence
This file has no implementation state. It defines operation ordering and persistence semantics for implementors: writes are staged in a batch, log data is WAL-only and does not consume sequence numbers, savepoints can roll back staged entries, and `getWriteBatch` exposes the underlying batch for DB writes.

## Dependencies and Integration Points
Depends on `ByteBuffer`, `ColumnFamilyHandle`, `RocksDBException`, `Status`, `Experimental`, and `WriteBatch`. It is the shared API implemented by abstract/native batch classes and used by higher-level transaction code.

## Risks and Test Signals
The contract documents undefined behavior for misuse of `singleDelete`; direct buffer methods require buffers whose position/limit define key/value slices. `AbstractTransactionTest` heavily exercises batch-like operations through transactions, including byte arrays, parts arrays, direct and heap `ByteBuffer`, column families, savepoints, and log data.
