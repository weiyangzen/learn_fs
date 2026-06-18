# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/BatchOperationHandler.java

## Purpose
`BatchOperationHandler` defines the store-level contract for creating and committing database batch operations.

## Important APIs and Types
`initBatchOperation()` returns a `BatchOperation` container. `commitBatchOperation(BatchOperation)` persists its collected operations and may throw `RocksDatabaseException`.

## Control Flow and State
The interface has no internal state. Implementations decide whether commits are synchronous, which write options apply, and how invalid operation types are handled.

## Persistence, Dependencies, and Integration
This interface is implemented by `DBStore`, with `RDBStore` returning `RDBBatchOperation` and committing through RocksDB write batches. It connects higher-level metadata tables to backend atomic writes.

## Risks and Test Signals
The generic signature accepts any `BatchOperation`; `RDBStore` casts to `RDBBatchOperation`, so wrong implementation types fail at runtime. Tests should cover commit success, exception propagation, close-after-commit, and invalid operation type handling if exposed.
