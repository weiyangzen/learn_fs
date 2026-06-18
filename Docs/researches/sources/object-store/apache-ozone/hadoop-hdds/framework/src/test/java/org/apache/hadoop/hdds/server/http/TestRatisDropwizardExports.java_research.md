<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestRatisDropwizardExports.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestRatisDropwizardExports.java

Purpose: tests Prometheus export of Ratis Dropwizard metrics through `RatisDropwizardExports`.

Important APIs/types/functions: `SegmentedRaftLogMetrics`, `RatisMetricsUtils.getDropWizardMetricRegistry`, Dropwizard `MetricRegistry`, `Timer`, `RatisDropwizardExports.collectAndExportAsText`, and Ratis raft log metric `RAFT_LOG_SYNC_TIME`.

Control flow: creates a Ratis segmented raft log metrics instance, locates a timer in its Dropwizard registry, records timing events, constructs the exporter, writes Prometheus text to a writer, and asserts expected normalized metric output appears.

State and persistence behavior: metrics state is in-memory in a Dropwizard registry. No disk persistence.

Dependencies and integration points: integrates Apache Ratis metrics with Ozone's Prometheus export path and Dropwizard timer types.

Risks: metric names and registry internals are tied to Ratis versions. Export text assertions may require updates when normalization or Prometheus type mapping changes.

Test signals: confirms a Ratis timer can be discovered and exported with expected Prometheus text.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestRatisDropwizardExports.java -->
