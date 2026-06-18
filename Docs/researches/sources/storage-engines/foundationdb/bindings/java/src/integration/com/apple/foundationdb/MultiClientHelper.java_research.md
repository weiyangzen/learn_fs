# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/MultiClientHelper.java

## Purpose
`MultiClientHelper` centralizes multi-client integration-test setup by reading cluster file paths from `FDB_CLUSTERS` and opening one `Database` per configured cluster.

## Important APIs, Types, and Functions
It implements JUnit `BeforeAllCallback`, provides static `readClusterFromEnv`, and exposes package-private `openDatabases(FDB)`.

## Control Flow
`beforeAll` reads and caches cluster files before test execution. `openDatabases` lazily reads cluster files if needed, opens each cluster path with `fdb.open(arg)`, caches the resulting collection, and returns the same collection for later calls.

## State and Persistence Behavior
The helper persists `clusterFiles` and `openDatabases` in the helper instance for the class lifetime. It does not close databases and does not implement `AfterAllCallback`, despite comments in users saying the helper will close databases.

## Dependencies and Integration Points
It depends on the `FDB_CLUSTERS` environment variable using semicolon delimiters and on Java binding database open behavior. It is used by multi-client integration classes in this subset.

## Risks and Edge Cases
Missing `FDB_CLUSTERS` throws `IllegalStateException`. Open databases are not closed, so long-running suites can leak native handles. The cached collection can contain partially opened databases if an exception occurs mid-loop. The helper is not thread-safe, but most setup happens before concurrent workload execution.

## Test Signals
Tests using it signal correct multi-client configuration when they can open all configured cluster files and perform transactions through each `Database`.
