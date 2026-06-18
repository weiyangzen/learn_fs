# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/GetClientStatusIntegrationTest.java

## Purpose
This integration test checks that `Database.getClientStatus()` returns a meaningful healthy client status report from the Java binding.

## Important APIs, Types, and Functions
It uses `FDB.selectAPIVersion(ApiVersion.LATEST)`, `fdb.open()`, `Database.run`, `Transaction.getReadVersion`, `Database.getClientStatus`, and JUnit assertions.

## Control Flow
The test opens a database, runs a read-version transaction to force client initialization, then retrieves client status bytes, converts them to a string, and asserts the JSON-like text contains `"Healthy":true`.

## State and Persistence Behavior
It does not modify database key-value state. It depends on and observes client status state maintained by the native FDB client.

## Dependencies and Integration Points
It exercises the JNI `Database_getClientStatus` path, future byte-array result marshalling, and C API client status reporting. Unlike most integration tests here, it is not annotated with `RequiresDatabase`, so it assumes the test environment provides a reachable database.

## Risks and Edge Cases
String containment is a loose JSON validation and could fail on formatting/schema changes even if the client is healthy. Lack of `RequiresDatabase` means a missing cluster fails rather than skipping or producing the standardized health-check failure.

## Test Signals
Passing indicates the client can connect, complete a read-version transaction, and return a status document showing healthy state through the Java API.
