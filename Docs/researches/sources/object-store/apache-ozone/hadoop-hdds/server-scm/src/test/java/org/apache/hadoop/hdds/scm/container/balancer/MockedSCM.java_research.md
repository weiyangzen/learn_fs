# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/MockedSCM.java

## Purpose
`MockedSCM` is a reusable balancer test fixture that presents a mocked `StorageContainerManager` backed by a deterministic `TestableCluster`. It allows balancer tasks to run against realistic node, container, replica, placement, replication-health, move-manager, and service-state interfaces without starting a full SCM.

## Important APIs, Types, and Functions
The public surface includes `init`, `startBalancerTask`, `startBalancerTaskAsync`, `getMoveManager`, `getReplicationManager`, `getNodeManager`, `getStorageContainerManager`, `getCluster`, `getContainerManager`, `getPlacementPolicy`, and `getEcPlacementPolicy`. Internally it mocks `ContainerManager`, `SCMServiceManager`, `MoveManager`, `ReplicationManager`, `StatefulServiceStateManager`, and placement policies. `MockedPlacementPolicies` builds real placement policies through `ContainerPlacementPolicyFactory`.

## Control Flow and State Behavior
The constructor creates a mocked SCM, a `MockNodeManager` seeded from `TestableCluster.getDatanodeToContainersMap`, a container manager backed by the cluster's container and replica maps, a completed `MoveManager`, and a healthy `ReplicationManager`. `init` writes the balancer config into an `OzoneConfiguration`, creates service and placement fixtures, and wires `StorageContainerManager` getters. `startBalancerTask` constructs a `ContainerBalancerTask`, calls `run()`, and returns the task for inspection. `startBalancerTaskAsync` starts the task in a new thread and is used by status-info tests that observe intermediate states.

Persistent service state is emulated with an in-memory `Map<String, ByteString>` in `MockedServiceStateManager`; `saveConfiguration` stores bytes and `readConfiguration` retrieves them. Move operations default to `CompletableFuture.completedFuture(MoveResult.COMPLETED)`, while tests can override the mock for failure, timeout, or exception scenarios.

## Dependencies and Integration Points
`MockedSCM` integrates synthetic cluster topology with production `ContainerBalancer`, `ContainerBalancerTask`, placement validation, `ReplicationManager`, and `MoveManager` APIs. It is the shared fixture for datanode-limit and status-info suites.

## Risks and Test Signals
The main risk is fixture realism: because move and replication health are mocked healthy by default, tests using `MockedSCM` primarily validate balancer selection and accounting logic, not actual replication execution. Its value is high because it keeps placement policies real and exposes metrics, selected sources/targets, and iteration history after a task run.
