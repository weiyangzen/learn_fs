# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/WatchesIntegrationTest.java

## Purpose
This integration test validates watch behavior in the Java binding, including successful watch triggering, watch limit errors, and cleanup after cancellation or closing.

## Important APIs, Types, and Functions
The class uses `DatabaseOptions.setMaxWatches`, `Transaction.watch`, `CompletableFuture.orTimeout`, `CancellationException`, `CompletionException`, `NativeFuture.close`, and helper methods `ensureConnected`, `setTestKeys`, and `createTestWatch`.

## Control Flow
Each test opens a database, sets a watch limit, ensures the client is connected via read version, writes initial key values, creates watch futures either one per transaction or many in a single transaction, changes keys, and waits for expected completion or error. Over-limit tests expect FDB error code `1032`. Cleanup tests create 100 watches, cancel or close most of them, then verify the remaining watches can complete within the limit.

## State and Persistence Behavior
The tests write fixed prefixes such as `aaa`, `bbb`, `ccc`, `ddd`, and `eee` and leave final values in the database. Watch state is native client state controlled by watch futures and database watch limits.

## Dependencies and Integration Points
It strongly exercises JNI `Transaction_watch`, `NativeFuture` cancellation/close, FDB watch accounting, Java futures, external-client support, and `RequiresDatabase`.

## Risks and Edge Cases
Several tests share the `ddd` prefix, which can cause interference under parallel execution or failed cleanup. Timeouts are environment-sensitive; heavily loaded CI can trigger false failures. The over-limit tests accept the first failing future but do not assert every extra watch fails deterministically.

## Test Signals
Passing indicates watch futures trigger on key changes, watch limits are enforced, and cancelled/closed watches release resources so later watches can complete.
