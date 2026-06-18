# sources/storage-engines/rocksdb/utilities/transactions/optimistic_transaction.cc

## Purpose
Implements RocksDB optimistic transactions, which track read/write keys and validate conflicts only at commit time instead of taking pessimistic locks during operations.

## Important APIs, Types, And Functions
Implements constructor, `Initialize`, `Reinitialize`, destructor, `Prepare`, `Commit`, `CommitWithSerialValidate`, `CommitWithParallelValidate`, `Rollback`, `TryLock`, `CheckTransactionForConflicts`, and `SetName`. `OptimisticTransactionCallback` invokes validation from the writer callback path.

## Control Flow
`TryLock` does not acquire a real lock. It sets a snapshot if needed, chooses the snapshot sequence or latest sequence, and records the key in the point lock tracker. `Commit` dispatches by validation policy. Serial validation uses `DBImpl::WriteWithCallback`, causing conflict checks on the writer thread before applying the write batch. Parallel validation locks deterministic OCC hash buckets for all tracked keys, checks conflicts cache-only, writes the batch, and unlocks with `Defer`.

## State And Persistence Behavior
Transaction state is inherited from `TransactionBaseImpl`: write batch, tracked locks, snapshot, and options. Successful commit writes the batch to RocksDB and clears transaction state. Rollback only clears local state. No prepared or named optimistic transaction state exists.

## Dependencies And Integration Points
Uses `OptimisticTransactionDBImpl`, `DBImpl`, `TransactionUtil::CheckKeysForConflicts`, `PointLockTrackerFactory`, `WriteCallback`, and OCC lock buckets. Conflict detection depends on memtable history retained by the DB options.

## Risks And Edge Cases
Two-phase commit and transaction names are unsupported. Cache-only validation can return retry-like failures if history is insufficient. Parallel validation locks raw mutex pointers and notes exception safety concerns. `exclusive` is tracked but not used for immediate locking.

## Test Signals
`optimistic_transaction_test.cc` should cover write-write and read-write conflicts, serial vs parallel validation, old transaction reuse, rollback clearing, unsupported prepare/name, and insufficient history behavior.
