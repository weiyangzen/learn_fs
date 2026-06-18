# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeDecommissionMetrics.java

Purpose: `NodeDecommissionMetrics` publishes aggregate and per-host metrics for decommission and maintenance workflows. It tracks monitored nodes, recommissioning nodes, pipelines waiting to close, under-replicated containers, unclosed containers, sufficiently replicated containers, and workflow start times.

Important APIs and types: The class is a Hadoop `MetricsSource` annotated with `@Metrics`. Public methods include `create`, `getMetrics`, `unRegister`, setter/getter pairs for aggregate gauges, and `metricRecordOfContainerStateByHost`. The nested `ContainerStateInWorkflow` holds per-host counters and `MetricsInfo` descriptors.

Control flow: `create()` registers the metrics source with `DefaultMetricsSystem`. `DatanodeAdminMonitorImpl` periodically sets aggregate gauges and replaces the per-host map. `getMetrics` snapshots aggregate gauges into one record, then emits additional tagged records for each host in `metricsByHost`.

State and persistence behavior: Metrics are in-memory only and reset on SCM restart. The per-host map is copied from monitor snapshots, not incrementally accumulated. `unRegister` removes the source from the metrics system during manager shutdown.

Dependencies and integration points: It integrates monitor progress with Hadoop metrics2, Ozone metrics context, JMX/metrics sinks, and tests through visible getters.

Risks: `getMetrics` manually chains records with `endRecord`; changes must preserve metrics2 expectations. The per-host map key is host string, so duplicate hostnames or hostname changes can overwrite records. All mutating methods are synchronized, limiting races but making long metrics collection a possible contention point.

Test signals: Tests should verify registration/unregistration, aggregate gauge setters/getters, per-host metric replacement, missing-host visible getters returning null, and metrics snapshot containing both aggregate and tagged host records.
