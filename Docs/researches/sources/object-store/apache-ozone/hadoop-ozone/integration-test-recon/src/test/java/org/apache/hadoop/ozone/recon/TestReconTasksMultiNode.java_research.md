# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconTasksMultiNode.java

## Purpose

This class provides additional multi-node ContainerHealthTask checks using a shared three-datanode cluster. It is separated from `TestReconTasks` because the cluster lifecycle and timing configuration differ.

## Important APIs, types, and functions

The suite uses `MiniOzoneCluster`, `ReconService`, `ReconStorageContainerManagerFacade`, `ReconContainerManager`, `PipelineManager`, `ContainerHealthSchemaManager.UnhealthyContainerRecord`, and `ContainerSchemaDefinition.UnHealthyContainerStates`. Test methods are `testContainerHealthTaskUnderReplicated()` and `testContainerHealthTaskOverReplicated()`.

## Control flow, state, and persistence

Setup creates a three-datanode cluster with five-second container and pipeline reports, ten-second missing-container task interval, and six/eight-second stale/dead intervals. Before each test it clears all unhealthy records and waits for Recon pipeline state. The tests wait for RF3 or RF1 pipelines and then query the unhealthy-container table for `UNDER_REPLICATED` or `OVER_REPLICATED`, expecting no rows in normal operation.

## Dependencies and integration points

The class verifies the query surface for unhealthy-container records in a multi-node Recon cluster, but it does not induce actual under- or over-replication. The comments point to more complete end-to-end coverage in `TestReconTasks`.

## Risks and test signals

These are low-depth smoke tests: they prove table access and normal healthy-cluster emptiness, not detection logic. The risk is false confidence because no unhealthy state is created. Positive signals are successful pipeline readiness and empty query results for both states after clearing the unhealthy table.
