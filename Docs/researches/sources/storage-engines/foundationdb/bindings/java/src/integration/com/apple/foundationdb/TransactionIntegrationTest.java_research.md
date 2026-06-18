# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/TransactionIntegrationTest.java

## Purpose
`TransactionIntegrationTest` verifies Java-binding behavior when operations are attempted after a transaction commit has been submitted or completed.

## Important APIs, Types, and Functions
It uses `FDB`, `Database`, `Transaction`, `CompletableFuture<Void>`, `CompletionException`, `FDBException`, and error code `2017` (`used_during_commit`).

## Control Flow
The test opens a database and repeats ten transactions. Each transaction writes `key1`, starts `commit`, attempts a read and a second commit that should fail with `used_during_commit`, waits for the original commit to succeed, then repeats the same invalid operation checks after commit completion.

## State and Persistence Behavior
The test writes `key1=val1` repeatedly and attempts `key2=val2` after commit submission, expecting that write to have no effect. It does not clear written state.

## Dependencies and Integration Points
It exercises Java transaction state guarding, native commit future behavior, error propagation through `CompletableFuture`, and `RequiresDatabase`.

## Risks and Edge Cases
`expectUsedDuringCommitError` assumes the thrown `CompletionException` cause is always `FDBException`; other exception shapes would cause `ClassCastException` rather than a clean assertion. The test does not verify that `key2` was not committed, only that a later commit attempt fails.

## Test Signals
Passing indicates Java transactions prevent additional native operations once commit is in flight or completed and propagate the expected FDB error code.
