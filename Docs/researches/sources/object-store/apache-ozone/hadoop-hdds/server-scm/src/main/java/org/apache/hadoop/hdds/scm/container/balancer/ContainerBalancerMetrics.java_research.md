<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerMetrics.java

## Purpose
Defines Hadoop Metrics2 counters for container balancer progress, latest-iteration results, cumulative move outcomes, unbalanced data size, and datanode involvement.

## Important APIs, Types, And Functions
`ContainerBalancerMetrics.create()` registers a Metrics2 source named `ContainerBalancerMetrics`. Counters include scheduled, completed, timeout, failed, data moved in bytes and GB, iteration count, datanodes involved, unbalanced GB, and unbalanced datanodes. Reset methods subtract current latest-iteration values. `incrementCurrentIterationContainerMoveMetric` maps `MoveManager.MoveResult` values to completed, timeout, or failed counters.

## Control Flow
The balancer task resets latest-iteration counters at the start of each iteration, increments scheduled counts when moves are submitted, increments result counters in move completion callbacks, and folds latest counters into cumulative counters at iteration end.

## State And Persistence
Metrics are process-local Hadoop Metrics2 mutable counters. They are not persisted across SCM restart. The `ms` field stores the metrics system reference but this class has no unregister method.

## Dependencies And Integration Points
Depends on Hadoop Metrics2 annotations, `DefaultMetricsSystem`, `MutableCounterLong`, and `MoveManager.MoveResult`. It is used by `ContainerBalancer` and `ContainerBalancerTask`, and status-info helper classes read its values.

## Risks And Test Signals
Using counters as resettable gauges by incrementing negative values requires accurate current values and can underflow if externally manipulated. GB and byte metrics are both tracked and can diverge if update order changes. Result classification must stay aligned with `MoveManager.MoveResult` enum additions. Tests should cover resets, cumulative folding, classification of completed/timeout/failure results, scheduled counters, and repeated metrics registration behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerMetrics.java -->
