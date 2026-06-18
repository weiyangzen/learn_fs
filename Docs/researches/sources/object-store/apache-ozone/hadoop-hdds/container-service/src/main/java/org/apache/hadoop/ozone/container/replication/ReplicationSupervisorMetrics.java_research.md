# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ReplicationSupervisorMetrics.java

Purpose: exposes `ReplicationSupervisor` counters and gauges through Hadoop Metrics2.

Important APIs and functions: `create` registers a new metrics source in the default metrics system. `unRegister` removes it. `getMetrics` emits total in-flight, queued, requested, success, failure, timeout, skipped, and max-stream gauges. It also iterates `ReplicationSupervisor.getMetricsMap()` to publish per-task metric families and emits per-task-class in-flight gauges.

Control flow and state: the class is a thin adapter over live supervisor getter methods. It has no internal counters.

Dependencies and integration: used by datanode metrics registration for replication visibility. It depends on Metrics2 `MetricsCollector`, `Interns`, and `DefaultMetricsSystem`.

Risks and test signals: metric name construction is dynamic and can collide if metric names are reused poorly. Tests should verify registration/unregistration, empty metrics map behavior, per-type gauges, and values matching supervisor counters after success, failure, skipped, and timeout runs.
