# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestKeyPurging.java

## Purpose
`TestKeyPurging` verifies that OM's `KeyDeletingService` processes deleted keys and purges pending-deletion metadata. It uses a live MiniOzoneCluster with short heartbeat, container-report, and block-deleting intervals.

## Important APIs, Types, and Functions
- `setup()` configures fast background service intervals, starts a three-datanode cluster, opens an RPC client, and records the `OzoneManager`.
- `testKeysPurgingByKeyDeletingService()` creates a volume/bucket, writes ten 100-byte keys, deletes them, waits for `KeyDeletingService` progress, and checks pending-deletion keys are empty.
- `shutdown()` closes the client and cluster.

## Control Flow
The test writes fixed data to ten keys through `TestDataUtil.createKey`, deletes each key, obtains `KeyManager.getDeletingService()`, waits until deleted-key count reaches ten, asserts the service has run more than once, then repeatedly calls `getPendingDeletionKeys(...).getPurgedKeys()` until it is empty.

## State and Persistence Behavior
The test relies on deleted-key metadata being created when keys are deleted and then purged by the background deleting service after SCM/container reports advance. It observes service counters and pending-deletion query results.

## Dependencies and Integration Points
Dependencies include MiniOzoneCluster, Ozone client APIs, `KeyManager`, `KeyDeletingService`, block-deleting interval config, heartbeat/container report config, `GenericTestUtils.waitFor`, and `ContainerTestHelper` data generation.

## Risks and Test Signals
Risks include timing sensitivity in background services and cluster reports. Signals are deleted-key count reaching `NUM_KEYS`, service run count greater than one, and no pending purged keys returned by the key manager.
