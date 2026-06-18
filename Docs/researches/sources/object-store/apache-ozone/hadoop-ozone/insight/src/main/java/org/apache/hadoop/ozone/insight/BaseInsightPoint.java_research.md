<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/BaseInsightPoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/BaseInsightPoint.java

Purpose: abstract default implementation of `InsightPoint` that supplies empty metric/config/logger catalogs plus common helper methods for SCM access, log level defaults, RPC metric descriptors, protobuf message counters, and log filtering.

Important APIs: `getMetrics`, `getConfigurationClasses`, and `getRelatedLoggers` return empty lists for subclasses to override. `createScmClient(OzoneConfiguration)` validates `ozone.scm.client.address` and returns a `ContainerOperationClient`. `defaultLevel(verbose)` maps verbose mode to TRACE and normal mode to DEBUG. `addProtocolMessageMetrics` creates one `MetricDisplay` per protobuf enum value filtered by `type`. `addRpcMetrics` defines common Hadoop RPC Prometheus metrics with a caller-supplied servername filter. `filterLog` requires each `filters` entry to appear as `[key=value]` in the log line.

Control flow: insight subclasses call metric helpers while building display groups. Pipeline-backed datanode insight calls `createScmClient`, which fails early if SCM client address is missing. Log streaming calls `filterLog` for post-selection filtering.

State and persistence: stateless except for local descriptor construction. No persistence. It depends on live SCM configuration only when creating an SCM client.

Dependencies and integration: HDDS configuration and SCM client classes, `ContainerOperationClient`, `MetricGroupDisplay`, `MetricDisplay`, `Component`, and `LoggerSource.Level`. Prometheus metric names are hardcoded and must stay aligned with Ozone metric exporters.

Risks and tests: `filterLog` uses regex with raw filter keys/values, so regex metacharacters in values can alter matching. It returns true for an empty map. `createScmClient` depends on `ozone-site.xml` containing SCM client address. `TestBaseInsightPoint` covers single, empty, and multi-filter log matching; helper metric builders and SCM client creation are not directly tested.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/BaseInsightPoint.java -->
