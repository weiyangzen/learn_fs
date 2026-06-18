# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconScmSnapshot.java

## Purpose

This test validates Recon's SCM snapshot download and node-manager persistence behavior. It verifies that Recon can refresh containers, pipelines, and node DB state from SCM after being stopped, and that explicit node removal updates both persistent and in-memory node tracking.

## Important APIs, types, and functions

The class uses `MiniOzoneCluster`, `ReconService`, `ReconStorageContainerManagerFacade`, `ReconNodeManager`, `ContainerManager`, `PipelineManager`, `NodeStatus`, and `LogCapturer`. Test methods are `testScmSnapshot()` and `testExplicitRemovalOfNode()`.

## Control flow, state, and persistence

Setup enables SCM snapshot support, sets a zero container threshold to force snapshot behavior, and configures short heartbeat, stale, and dead-node intervals. `testScmSnapshot()` records Recon's initial empty container view and node DB key count, stops Recon, allocates ten SCM containers, restarts Recon, and compares SCM and Recon container/pipeline counts. It also checks that node DB key count remains stable. `testExplicitRemovalOfNode()` stops one datanode, waits for DEAD status, verifies the node remains tracked, then calls `removeNode()` and verifies DB and memory counts drop to three.

## Dependencies and integration points

The test integrates Recon restart lifecycle, SCM metadata snapshot transfer, Recon node DB persistence, and heartbeat-driven node status transitions. Log capture on `ReconStorageContainerManagerFacade` is used as an additional signal that container count comparison happened.

## Risks and test signals

Timing depends on heartbeat and dead-node intervals; `GenericTestUtils.waitFor()` bounds the node-death wait. The snapshot test assumes the restart path reinitializes Recon storage managers against the same mini-cluster SCM. Positive signals are SCM/Recon container count equality, pipeline count equality, unchanged node DB count after snapshot refresh, and explicit removal reducing both DB key count and `getAllNodes()` size.
