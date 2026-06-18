<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/SCMPipelineMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/SCMPipelineMetrics.java

Purpose: `SCMPipelineMetrics` exposes SCM pipeline-manager counters and latency metrics through Hadoop Metrics2. It tracks pipeline allocation, creation, destruction, report handling, duplicate-datanode-pipeline detection, per-pipeline block allocations, and creation latency.

Important APIs and types: Static lifecycle methods are `create` and `unRegister`. Runtime methods include `createPerPipelineMetrics`, `removePipelineMetrics`, `incNumBlocksAllocated`, the `incNumPipeline...` counters, `updatePipelineCreationLatencyNs`, `getTotalNumBlocksAllocated`, and `getMetrics`. It uses `MetricsRegistry`, `MutableCounterLong`, `MutableRate`, `DefaultMetricsSystem`, and `Interns.info`.

Control flow: `create` registers a singleton metrics source. `getMetrics` snapshots global counters and every per-pipeline counter into the collector. Per-pipeline counters are created with names that encode pipeline type, replication config, and pipeline ID.

State and persistence behavior: Metrics are process-local and not persisted. `numBlocksAllocated` is a `ConcurrentHashMap`, so per-pipeline metric mutation can proceed concurrently with snapshots and pipeline cleanup.

Dependencies and integration points: Pipeline manager code calls these methods during lifecycle transitions, report processing, and block allocation. Metrics names are externally visible to monitoring systems.

Risks: Singleton lifecycle means tests must unregister to avoid leaked state. Per-pipeline metric cardinality can grow if removal is missed. `incNumBlocksAllocated` silently ignores missing pipeline metrics, which avoids failures but can hide lifecycle ordering bugs.

Test signals: Metrics tests should assert singleton reuse, source unregister, counter increments, per-pipeline metric names, total block allocation sums, latency updates, and removal of closed pipeline counters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/SCMPipelineMetrics.java -->
