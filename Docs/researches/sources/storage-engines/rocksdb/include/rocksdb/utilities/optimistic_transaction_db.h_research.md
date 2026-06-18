# sources/storage-engines/rocksdb/include/rocksdb/utilities/optimistic_transaction_db.h

## Purpose
Declares the optimistic transaction DB wrapper, where conflicts are validated at commit instead of using pessimistic locks during normal operations.

## Important APIs, Types, And Functions
`OptimisticTransactionOptions`, `OccValidationPolicy`, `OccLockBuckets`, `MakeSharedOccLockBuckets`, `OptimisticTransactionDBOptions`, and `OptimisticTransactionDB::Open`/`BeginTransaction` define the public surface.

## Control Flow, State, And Persistence
Open wraps a base DB. Transactions collect writes and tracked reads in an indexed batch. Commit validates conflicts serially or in parallel depending on OCC policy, then writes atomically on success. State is transient until commit; shared lock buckets are process-memory coordination structures.

## Dependencies And Integration Points
Depends on `Comparator`, `DB`, `Transaction`, and `StackableDB`. Integrates with `transaction.h`, `WriteBatchWithIndex`, and validation tuning.

## Risks And Edge Cases
Range deletions are incompatible. Non-default comparators must be supplied in transaction options. Parallel validation trades less write-group contention for lock bucket memory and ordering complexity. Reused transaction handles may retain allocations.

## Test Signals
Cover conflict detection, snapshot validation, serial/parallel policies, shared lock buckets, custom comparator behavior, range-delete rejection, and transaction handle reuse.
