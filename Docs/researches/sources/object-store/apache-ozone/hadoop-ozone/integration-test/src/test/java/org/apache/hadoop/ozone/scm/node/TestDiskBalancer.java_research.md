# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/scm/node/TestDiskBalancer.java

## Purpose
`TestDiskBalancer` validates direct client-to-datanode disk balancer RPCs for report retrieval, start/stop-after-even behavior, status reporting, and pause/resume around datanode decommission/recommission.

## Important APIs, Types, and Functions
The test starts a 3-DN mini cluster with `SCMContainerPlacementCapacity`, updates node storage reports with random reports, creates `DiskBalancerProtocolClientSideTranslatorPB` proxies to each DN `CLIENT_RPC` port, and uses `DiskBalancerConfigurationProto`, `DatanodeDiskBalancerInfoProto`, and `DiskBalancerRunningStatus`. It also uses `ContainerOperationClient` to decommission and recommission nodes.

## Control Flow, State, and Persistence
`testDatanodeDiskBalancerReport` queries each DN for disk balancer info and checks volume density and node metadata. `testDiskBalancerStopAfterEven` starts balancing on one DN with `stopAfterDiskEven=true`, observes `RUNNING`, then waits for `STOPPED`. `testDatanodeDiskBalancerStatus` starts balancing on all DNs, verifies `RUNNING`, decommissions one DN, waits for that DN to become `PAUSED`, confirms other in-service DNs remain `RUNNING`, recommissions the DN, and waits for `RUNNING` again. State under test is live DN disk balancer service state and SCM operational state.

## Dependencies and Integration Points
The file connects SCM node manager state, DN client RPC, disk balancer service configuration, placement policy, storage reports, and decommission/recommission workflows.

## Risks and Test Signals
Risks include timing sensitivity in service transitions and random storage report shape. Signals are direct RPC status reads from DNs and SCM node state waits, covering behavior not visible through SCM-only APIs.
