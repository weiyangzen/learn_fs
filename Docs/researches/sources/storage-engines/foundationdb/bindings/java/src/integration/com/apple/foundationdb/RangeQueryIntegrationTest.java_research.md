# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/RangeQueryIntegrationTest.java

## Purpose
This integration test verifies Java range-query behavior against a live FoundationDB cluster, covering key selectors, inclusive/exclusive ranges, empty scans, and multi-row scans.

## Important APIs, Types, and Functions
It uses `RequiresDatabase`, `Database.run`, `Transaction.clear`, `Transaction.set`, `Transaction.get`, `Transaction.getRange`, `KeySelector`, `AsyncIterable`, `AsyncIterator`, `KeyValue`, and `ByteArrayUtil`.

## Control Flow
`clearDatabase` runs before and after each test, retrying a full database clear up to five times. Individual tests load small data sets, then run transactions that read exact keys or iterate range query results and assert keys/values/counts. The key-selector test generates a random key with a fixed first byte and scans the range for that leading byte.

## State and Persistence Behavior
The setup/teardown clears the full keyspace `[empty, 0xff)`, which is safe only for isolated test clusters. Within tests, state is simple test key-value data written and then cleared.

## Dependencies and Integration Points
It exercises JNI `get`, `getRange`, range iterator Java logic, tuple-independent byte-array comparison, and the live database health gate. It also depends on transaction retry behavior for clearing under heavy CI load.

## Risks and Edge Cases
Full database clears are destructive if run against a non-test cluster. The range `"multi"` to `"multj"` assumes ASCII lexicographic ordering around generated keys. Only 100 rows are used, which may or may not force multiple batches depending on client/server behavior.

## Test Signals
Passing indicates basic range scanning and key selector marshalling work end-to-end through the Java binding and native client.
