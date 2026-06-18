# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/BasicMultiClientIntegrationTest.java

## Purpose
This integration test verifies that multiple FoundationDB client instances can write and read data through the Java API when configured by `MultiClientHelper`.

## Important APIs, Types, and Functions
The class uses JUnit 5, `@RegisterExtension MultiClientHelper`, `FDB.selectAPIVersion(630)`, database options, `Database.run`, `Transaction.set`, `Transaction.get`, and `Tuple` packing/unpacking.

## Control Flow
The test selects API version 630, sets a low trace severity knob, opens one `Database` per cluster file from `FDB_CLUSTERS`, then loops 25 times. For each opened database it writes a random tuple key/value pair in one transaction, reads the key in a second transaction, unpacks the value, and asserts equality. A short sleep separates outer iterations.

## State and Persistence Behavior
It persists random keys into every configured cluster and does not clear them afterward, so repeated runs leave test data behind. Database handles are owned by the helper and reused for the test class.

## Dependencies and Integration Points
It depends on a configured multi-client environment, `FDB_CLUSTERS`, the native external client stack, and tuple encoding. The `MultiClient` tag is used to exclude it from ordinary single-client test runs.

## Risks and Edge Cases
The test uses random keys without a test namespace, creating possible collisions with other tests or previous runs, though the wide random space lowers the chance. It does not close databases itself and relies on helper behavior, but `MultiClientHelper` in this subset does not implement an after-all close callback. It selects a fixed API version rather than `ApiVersion.LATEST`.

## Test Signals
Passing indicates basic cross-client open/write/read behavior, tuple round-trip, and transaction retries through `Database.run` are functional in a multi-client setup.
