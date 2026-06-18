# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/CycleMultiClientIntegrationTest.java

## Purpose
This standalone multi-client integration workload tests transaction atomicity by maintaining a four-node directed cycle while concurrent writers transform edges and concurrent checkers validate cycle invariants.

## Important APIs, Types, and Functions
The file defines `CycleMultiClientIntegrationTest`, nested `CycleWorkload`, nested `CycleChecker`, and constants controlling transaction counts and thread count. It uses `FDB.selectAPIVersion(ApiVersion.LATEST)`, `MultiClientHelper`, `FDBOptions` for client threading/external client directory/tracing/knobs, `Database.run`, and tuple encoding.

## Control Flow
`main` selects FDB, configures one client thread per cluster file, opens all databases, initializes keys `0..3` as a cycle, starts writer threads for each database, then starts checker threads and waits for checkers to finish. Writers repeatedly pick a cycle node, read four linked values, and rewrite three edges to reverse part of the cycle. Checkers read four linked values from random starts, assert the fourth points back to the key, sort the observed values, and compare them with `[0,1,2,3]`.

## State and Persistence Behavior
The test writes un-namespaced tuple keys `"0"` through `"3"` to every configured database and leaves the final cycle state in place. Shared static state includes `expected` and helper instances. The checker success flag is per checker instance and read after thread join.

## Dependencies and Integration Points
It depends on external-client multi-cluster setup through `/var/dynamic-conf/lib` and `FDB_CLUSTERS`. It is not a JUnit `@Test`; it is a main-driven workload likely intended for specialized multi-client execution.

## Risks and Edge Cases
Un-namespaced keys are invasive. Writer threads are not joined, so they may still be running while checkers validate and when the program exits. Exceptions inside worker threads are not captured as explicit failures unless they affect the success flag. The read of `succeed` is safe after `join`, but the flag is not volatile for any earlier observation.

## Test Signals
Passing checkers indicate observed transaction snapshots preserve cycle invariants under concurrent transactional rewrites across multi-client database handles.
