# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestCloseContainer.java

## Purpose

`TestCloseContainer` verifies close-container behavior across SCM, datanodes, restart, replica reporting, and checksum generation. It uses a three-datanode MiniOzoneCluster and real client writes to exercise control-plane and datanode state transitions.

## Important APIs, Types, And Functions

Setup tunes heartbeat/report intervals, starts `MiniOzoneCluster`, creates an `OzoneClient`, volume, and bucket. Tests use `OzoneTestUtils.closeContainers`, `StorageContainerManager`, `ContainerInfo`, `ContainerReplica`, `OzoneContainer`, and `ContainerMerkleTreeTestUtils`. Helpers include `getContainerReplicas` and `checkContainerCloseInDatanode`.

## Control Flow

`testReplicasAreReportedForClosedContainerAfterRestart` writes data, closes a container, restarts SCM, and waits for replica state to be reported after heartbeat/container reports resume. `testCloseClosedContainer` asserts idempotent handling when closing an already closed container. `testContainerChecksumForClosedContainer` writes keys, closes containers, waits for datanodes to close them, and checks checksum files for closed containers.

## State And Persistence Behavior

The test mutates OM key state, SCM container lifecycle state, datanode container state, replica reports, and checksum files on datanode storage. Restart verifies persistence of SCM metadata and subsequent reconciliation from datanode reports.

## Dependencies And Integration Points

It integrates Ozone client writes, SCM container manager, replication manager, datanode state machines, container checksums, and MiniOzoneCluster lifecycle.

## Risks And Test Signals

Race sensitivity is high because close and report processing are asynchronous. Failures signal lifecycle idempotency bugs, lost replica reports after restart, checksum-generation regressions, or stale container state on datanodes.
