# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerMoveInfo.java

Purpose: value object containing latest-iteration container move counters for scheduled, completed, failed, and timed-out moves.

Important APIs: direct long constructor; metrics constructor reading `ContainerBalancerMetrics` latest-iteration counters; four getters. No setters, persistence, or background behavior.

Control flow and state: construction snapshots counter values. The direct constructor is useful for tests and synthetic reports; the metrics constructor integrates with live balancer metrics.

Dependencies and integration: used by `ContainerBalancerTaskIterationStatusInfo` and balancer status reporting. Tests in `TestContainerBalancerStatusInfo` indirectly validate fields as part of current and historical iteration status.

Risks: no validation prevents negative counters if supplied by a bad caller; metrics constructor assumes metrics object is non-null and already initialized. Test signals should check both constructors and consistency with `ContainerBalancerMetrics` reset/iteration boundaries.
