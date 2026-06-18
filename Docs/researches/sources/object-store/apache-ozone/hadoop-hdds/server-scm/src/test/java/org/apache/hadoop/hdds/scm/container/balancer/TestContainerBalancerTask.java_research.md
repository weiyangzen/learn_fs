# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancerTask.java

## Purpose
`TestContainerBalancerTask` is a focused balancer-task unit suite using an internally generated 10-node cluster. It validates node include/exclude filtering, configuration parsing, delayed task startup, source requeue behavior after move failures, and exclusion of zero-size containers.

## Important APIs, Types, and Functions
The fixture constructs `ContainerBalancerTask`, `ContainerBalancer`, `ContainerBalancerConfiguration`, `MoveManager`, `ContainerManager`, `ReplicationManager`, `MockNodeManager`, placement policies, `DatanodeUsageInfo`, `ContainerInfo`, and `ContainerReplica`. Helper methods `generateUtilizations`, `generateData`, `createCluster`, `createReplicasForContainers`, `createContainer`, `createReplica`, and `startBalancer` build and run a synthetic cluster. Containers alternate between RATIS and EC replication based on ID parity.

## Control Flow and State Behavior
`setup()` creates mocked SCM dependencies, a completed `MoveManager`, healthy replication-manager responses, in-memory service-state persistence, real placement policies from a `MockNodeManager`, and a `ContainerBalancerTask` configured for one iteration with full datanode involvement. `generateData` creates 10 datanodes with increasing utilization, assigns containers of varying used sizes, and records container-to-replica and datanode-to-container maps. `createCluster` computes node capacity from target utilization and used bytes, then sets `SCMNodeStat` values on each `DatanodeUsageInfo`.

`balancerShouldFollowExcludeAndIncludeDatanodesConfigurations` configures include and exclude node lists using IPs and hostnames, runs the task, and verifies every selected source and target belongs to included-minus-excluded nodes. `testContainerBalancerConfiguration` reads storage and time settings through the config object and checks threshold, max source-leaving size, move timeout, and replication timeout parsing.

`testDelayedStart` starts a task thread with delayed startup enabled, waits until the thread is sleeping, interrupts it, and asserts STOPPED status and thread death. `testSourceDatanodeAddedBack` and `testSourceDatanodeAddedBackForReplicationNotHealthyBeforeMove` make the first move fail with retryable move results, then complete the second move; they assert two datanodes are involved, one failed move is counted, at least one move completes, and the source/target sets contain the expected endpoints. `balancerShouldMoveOnlyPositiveSizeContainers` uses a special size array for that test and asserts no selected container has non-positive used bytes.

## Dependencies and Integration Points
This file integrates task-level balancing logic with placement policy construction, mocked replication health, move manager futures, node statistics, and Ozone configuration parsing. It overlaps conceptually with `TestContainerBalancerDatanodeNodeLimit` but uses a local cluster generator rather than `TestableCluster`.

## Risks and Test Signals
Risks covered include ignoring include/exclude node filters, parsing size/time config incorrectly, leaving delayed threads running, abandoning sources after retryable move failures, and scheduling zero-byte containers. Signals are selected source/target maps, metric counters, task status, thread state, and parsed configuration values.
