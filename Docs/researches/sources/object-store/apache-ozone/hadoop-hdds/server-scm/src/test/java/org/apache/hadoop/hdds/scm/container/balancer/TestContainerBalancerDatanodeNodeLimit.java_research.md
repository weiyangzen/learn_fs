# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancerDatanodeNodeLimit.java

## Purpose
`TestContainerBalancerDatanodeNodeLimit` is a parameterized `ContainerBalancerTask` suite that runs the same behavioral checks across synthetic clusters from 4 to 30 datanodes. It focuses on datanode involvement limits, movement size limits, utilization calculation, container eligibility, placement policy, target health, include/exclude container filters, iteration results, and move-result accounting.

## Important APIs, Types, and Functions
The suite uses `MockedSCM`, `TestableCluster`, `ContainerBalancerConfigBuilder`, `ContainerBalancerTask`, `ContainerBalancerMetrics`, `MoveManager`, `ContainerInfo`, `ContainerReplica`, `DatanodeUsageInfo`, and placement policy APIs. Utility methods include `createMockedSCMs`, `getMockedSCM`, `getUnBalancedNodes`, `stillHaveUnbalancedNodes`, `genCompletableFuture`, and `genCompletableFutureWithException`.

## Control Flow and State Behavior
Each parameterized test receives a fresh `MockedSCM`, builds a configuration, runs `mockedSCM.startBalancerTask(config)`, and inspects the completed task and metrics. Datanode-limit tests compare `getCountDatanodesInvolvedPerIteration` and `metrics.getNumDatanodesInvolvedInLatestIteration` to `maxDatanodesPercentageToInvolvePerIteration * nodeCount / 100`. Size-limit tests lower `maxSizeEnteringTarget` or `maxSizeLeavingSource` so no container can be selected, then rerun with defaults to prove movement resumes.

The suite verifies threshold-driven unbalanced-node selection against `TestableCluster.getUnBalancedNodes`, checks average-utilization math, and confirms the balancer calls `MoveManager.move`. Eligibility tests mutate all containers to OPEN or all replicas to CLOSING and assert no movement occurs. Selection tests assert moved containers are CLOSED, target datanodes do not already host the selected container, placement policy remains satisfied after source-to-target substitution, targets are in-service healthy, and a container is not selected more than once.

Include/exclude container filters are tested through `setExcludeContainers` and `setIncludeContainers`. Iteration-result tests validate `ITERATION_COMPLETED` under normal moves, failed moves, explicit future timeouts, replication-manager timeout results, and exceptions from `MoveManager`.

## Dependencies and Integration Points
The suite depends heavily on `MockedSCM` and real placement-policy validation. It also uses metrics, container manager maps, node manager status, and Ozone size constants.

## Risks and Test Signals
Risks include over-involving datanodes, violating movement caps, selecting ineligible containers or unhealthy targets, breaking placement, duplicate container moves, and miscounting timeouts/failures. Signals are task maps, selected source/target sets, metrics counters, movement sizes, and iteration result enums. Two tests are marked flaky for known HDDS issues, indicating timing and move-result accounting sensitivity.
