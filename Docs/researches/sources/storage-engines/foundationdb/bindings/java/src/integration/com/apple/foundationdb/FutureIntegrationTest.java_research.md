# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/FutureIntegrationTest.java

## Purpose
This integration test validates Java binding future cancellation and callback behavior for FDB reads, including callback execution using both the default executor and a direct executor.

## Important APIs, Types, and Functions
The file defines a `DirectExecutor`, four `@Test` methods tagged `SupportsExternalClient`, and a `testTransaction` helper. It uses `CompletableFuture`, `thenAcceptAsync`, `cancel`, `join`, `Database.run`, and `Transaction.get`.

## Control Flow
Each test passes a transaction lambda into `testTransaction`, which runs it ten times using a normal database and ten times using `fdb.open(null, new DirectExecutor())`. The scenarios cancel a future before use, cancel a future after setting a callback, register a callback after `join`, and cancel futures from inside a callback.

## State and Persistence Behavior
The tests read absent keys and do not write database state. State is limited to futures, callback queues, and executor behavior during each transaction.

## Dependencies and Integration Points
This is a direct signal for `NativeFuture` callback registration/cancellation, JNI callback execution, Java executor dispatch, and the transaction lifetime expectations around futures. It depends on `RequiresDatabase` to ensure a live cluster.

## Risks and Edge Cases
Callbacks are asynchronous; some lambdas may not be forced to complete before the transaction lambda returns unless cancellation or join triggers them. The tests assert callback values are null but do not capture failures from callbacks unless those failures propagate through the executor/future path. Direct executor coverage is valuable because it exercises reentrant callback behavior.

## Test Signals
Passing indicates cancellation does not crash, callbacks can be installed before and after readiness, and callback code can perform additional FDB operations or cancel related futures without deadlocking.
