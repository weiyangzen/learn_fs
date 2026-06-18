# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/DataNodeMetricsCollectionTask.java

Purpose: Callable that collects a datanode's pending deletion bytes through its JMX endpoint.

Important APIs: constructor builds a `MetricsServiceProvider` from `MetricsServiceProviderFactory`; `call` returns `DatanodePendingDeletionMetrics`; private `getJmxMetricsUrl` builds HTTP or HTTPS URL using datanode port metadata.

Control flow and state: `call` asks the metrics provider for bean `Hadoop:service=HddsDatanode,name=BlockDeletingService`, extracts `TotalPendingBlockBytes`, and returns host, UUID, and bytes. Empty or failed responses produce a metric record with `-1L`.

Dependencies and integration: uses `DatanodeInfo`, datanode HTTP/HTTPS ports, `ReconUtils.getMetricsData`, `ReconUtils.extractLongMetricValue`, and Recon's JMX metrics provider. Likely used by insight endpoints/tasks aggregating pending deletion backlog.

Risks: missing port values or unreachable JMX endpoints degrade to `-1L`, which callers must treat as unknown rather than real negative backlog. Bean/key names are string constants tied to datanode metrics implementation. The task logs failures at error level per datanode, which can be noisy during cluster-wide outages.

Test signals: mock metrics provider/factory to cover HTTP vs HTTPS URL construction, missing metrics, extraction success, provider exceptions, and absent bean fields.
