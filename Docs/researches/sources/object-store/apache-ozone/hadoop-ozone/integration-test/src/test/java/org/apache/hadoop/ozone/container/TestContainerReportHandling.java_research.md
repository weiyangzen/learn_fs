# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/TestContainerReportHandling.java

Purpose: This parameterized integration test verifies SCM handling of full container reports for non-empty replicas whose SCM container is already in `DELETING` or `DELETED`. It protects the rule that such replicas should be deleted when block commit sequence IDs are eligible for RATIS, while EC ignores the bcsid comparison.

Important APIs and types: The test uses `MiniOzoneCluster`, `OzoneClient`, `ReplicationConfig`, `TestHelper.ReplicationInput`, `TestDataUtil.createKey`, `OmKeyArgs`, `OmKeyInfo`, `ContainerID`, `ContainerManager`, `HddsProtos.LifeCycleState`, `HddsProtos.LifeCycleEvent`, `waitForContainerClose`, `waitForContainerStateInSCM`, and `GenericTestUtils.waitFor`.

Control flow: `delStatesAndReplication` creates four cases from `DELETING` and `DELETED` crossed with RATIS and EC replication inputs. The test creates a cluster sized for the selected replication type, writes a small key, looks up the key's first location, waits for the local and SCM container state to become closed, and then drives SCM state transitions manually through `ContainerManager.updateContainerState`. For the `DELETED` case it applies `DELETE` followed by `CLEANUP`. It restarts every datanode in the key pipeline to force full container reports, then waits until SCM's replica set for the container becomes empty.

State and persistence behavior: SCM's in-memory and persisted container state transitions from closed to deleting or deleted, while datanodes retain closed non-empty replicas until restart sends a report. The observable final state is that `ContainerManager.getContainerReplicas(containerID)` is empty. The test also records and deletes the cluster base directory in `finally`, ensuring local MiniOzone storage is cleaned even after failures.

Dependencies and integration points: It exercises OM key lookup, SCM lifecycle management, datanode restart and full report generation, SCM report processing, and delete-replica command scheduling. It depends on `TestHelper.ReplicationInput` for correct datanode counts and replication configs.

Risks: The test waits up to 180 seconds for replica cleanup and assumes datanode restarts reliably trigger full reports. It directly mutates SCM state with `ContainerManager`, which is intentional but bypasses higher-level deletion flows. The core assertion is SCM-side replica disappearance, not explicit datanode directory deletion.

Test signals: The key signals are non-empty initial replica sets, exact SCM lifecycle state after `DELETE` and optional `CLEANUP`, datanode restart for each pipeline node, and eventual empty SCM replica tracking for both RATIS and EC cases.
