# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerConfigBuilder.java

## Purpose
`ContainerBalancerConfigBuilder` is a small test helper for constructing `ContainerBalancerConfiguration` instances suitable for synthetic cluster-balancer tests. It centralizes defaults used by `TestContainerBalancerDatanodeNodeLimit` and related balancer fixtures.

## Important APIs, Types, and Functions
The class wraps `OzoneConfiguration.getObject(ContainerBalancerConfiguration.class)` and exposes two constructors plus `build()`. The no-configuration constructor creates a fresh `OzoneConfiguration`; the second constructor accepts an existing `OzoneConfiguration` so tests can preload settings such as container size. It depends on `TestContainerBalancerTask.STORAGE_UNIT` to express size limits.

## Control Flow and State Behavior
Construction mutates a `ContainerBalancerConfiguration` object with deterministic test defaults: `iterations=1`, `threshold=10`, `maxSizeToMovePerIteration=50GB`, and `maxSizeEnteringTarget=50GB`. For clusters smaller than `DATANODE_COUNT_LIMIT_FOR_SMALL_CLUSTER` (15), it sets `maxDatanodesPercentageToInvolvePerIteration=100` so small clusters are not artificially capped by percentage rounding. `build()` simply returns the configured object; there is no persistence layer or external I/O.

## Dependencies and Integration Points
The helper integrates with Ozone's configuration object mapping and the balancer test cluster sizes. It is intentionally package-private and belongs to the balancer test package, so production code does not depend on it.

## Risks and Test Signals
The main risk is hidden coupling: changing these defaults can alter many parameterized balancer tests at once. The small-cluster percentage override is particularly important because without it tests on 4-14 node clusters could fail due to low allowed datanode involvement rather than balancer logic. Test signal is indirect through the suites that consume the builder.
