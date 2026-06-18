# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/TransactionTest.java

## Purpose

This suite extends `AbstractTransactionTest` to validate transaction conflict detection, prepare/commit/rollback behavior, prepared-value visibility, multi-get variants, transaction metadata, and state transitions in Java.

## Important APIs and types

The file uses `TransactionDB`, `Transaction`, `TransactionOptions`, `TransactionDBOptions`, `WriteOptions`, `ReadOptions`, `ColumnFamilyHandle`, `ColumnFamilyDescriptor`, `StringAppendOperator`, `Transaction.TransactionState`, and helper container types from `AbstractTransactionTest`.

## Control flow

Conflict tests write initial values, have one transaction call `getForUpdate` or `multiGetForUpdate`, then assert another transaction attempting to write the locked key receives `Status.Code.TimedOut`. Prepare tests write a committed base value, prepare an update, and then either commit or rollback while concurrent reads verify old/new visibility. Metadata tests cover transaction name, ID/getId, deadlock detection flag, waiting transactions, and state after commit/rollback. `startDb` opens a transaction DB with default and test column families and merge operators, returning a container that owns all handles/options.

## State and persistence behavior

The file exercises transactional write state, lock state, prepared state, committed visibility, and column-family-specific data. Transactions are temporary native objects, while committed writes persist in the DB for later reads within the same test.

## Dependencies and integration points

This suite integrates Java transaction APIs with native lock management, read-prepared semantics, column-family routing, multi-get conversions, merge operator option wiring, and handle cleanup.

## Risks and test signals

Risks include missed lock conflicts, prepared writes becoming visible too early, rollback state confusion, CF list/key array mismatches, and close-order leaks. Signals are timed-out status codes, exact old/new value assertions, null for missing multi-get entries, transaction metadata checks, and state enum equality.
