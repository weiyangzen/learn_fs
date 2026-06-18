# sources/storage-engines/rocksdb/utilities/transactions/optimistic_transaction_db_impl.h

## Purpose
Declares the concrete optimistic transaction DB wrapper and OCC lock bucket implementations used for parallel validation.

## Important APIs, Types, And Functions
`OccLockBucketsImplBase` extends public `OccLockBuckets` with `GetLockBucket`. `OccLockBucketsImpl<cache_aligned>` stores striped mutexes and reports memory usage. `OptimisticTransactionDBImpl` declares `BeginTransaction`, `DeleteRange`, `Write`, `GetValidatePolicy`, `GetLockBucket`, and private `ReinitializeTransaction`.

## Control Flow
The constructor records the validation policy and, for parallel validation, adopts shared lock buckets from options or creates default buckets with at least 16 stripes. `Write` rejects batches containing range deletes before delegating. `DeleteRange` is always unsupported.

## State And Persistence Behavior
The wrapper owns a base DB through `OptimisticTransactionDB`, a shared pointer to bucket locks when needed, and an immutable validation policy. Bucket locks are in-memory synchronization only.

## Dependencies And Integration Points
Depends on public optimistic transaction DB options, `Striped`, `CacheAlignedWrapper`, mutex utilities, and cast helpers. `OptimisticTransaction::CommitWithParallelValidate` calls `GetLockBucket` for every tracked key.

## Risks And Edge Cases
For serial validation, `bucketed_locks_` remains null and must not be used. Range deletion is rejected because optimistic conflict tracking is point-key based. Shared lock buckets allow cross-DB coordination only when users intentionally provide the same bucket object.

## Test Signals
Tests should cover memory usage reporting, shared bucket reuse, cache-aligned and regular bucket modes, parallel validation bucket locking, and range-delete rejection in both direct and batch writes.
