# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/Transaction.java

## Purpose
`Transaction` is the public read/write transaction interface combining read operations, write mutations, conflict-range control, commit/retry lifecycle, watches, and transaction-specific options.

## Important APIs, Types, And Functions
It extends `AutoCloseable`, `ReadTransaction`, and `TransactionContext`. Important methods include `getDatabase`, write and clear operations, conflict range/key methods, `mutate`, `options`, `commit`, committed version helpers, `getVersionstamp`, `getApproximateSize`, `watch`, `onError`, `cancel`, `close`, and direct `run`/`read` context methods.

## Control Flow
Client code builds operations on a transaction, calls `commit`, and on retryable failures calls `onError` to get a reset transaction. Database retry loops automate this sequence.

## State And Persistence Behavior
Implementations hold native transaction state: read version, read/write conflict ranges, mutations, options, watches, and commit status. Close disposes uncommitted native state.

## Dependencies And Integration Points
It integrates with `MutationType`, `TransactionOptions`, `Database`, tuple utilities, `Range`, `KeySelector`, and async contexts.

## Risks And Edge Cases
Transactions are invalid after `onError` in this binding. Unknown commit results can cause user code to be re-run. Watches and range iterators must be managed with transaction lifetime.

## Test Signals
Tests should cover writes, clears, atomic mutations, conflict range APIs, commit success/failure, retry with `onError`, versionstamp and committed version, watch cancellation, and close idempotence.
