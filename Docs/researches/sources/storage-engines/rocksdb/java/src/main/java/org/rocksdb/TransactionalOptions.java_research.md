# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionalOptions.java

## Purpose
`TransactionalOptions` is the small package-private interface shared by transaction option types. It captures snapshot-on-begin behavior while preserving fluent subtype returns.

## Important APIs and Types
The API has `isSetSnapshot()` and `setSetSnapshot(boolean)`. The generic self type `T extends TransactionalOptions<T>` lets setters return the concrete option type.

## Control Flow, State, and Persistence
There is no implementation or storage in this file. Implementors map the setting to native option state. Semantically, `setSetSnapshot(true)` is equivalent to calling `Transaction.setSnapshot()` after the transaction starts.

## Dependencies and Integration Points
It references `Transaction` in documentation and is used by `TransactionalDB<T>`, `TransactionOptions`, and likely optimistic transaction option classes.

## Risks and Test Signals
Risk is mainly semantic consistency across all implementors: snapshot timing must match `Transaction.setSnapshot()`. `AbstractTransactionTest` validates `setSnapshot`, `setSnapshotOnNextOperation`, `getSnapshot`, and `clearSnapshot` on transactions, providing indirect expectations for options that enable snapshots.
