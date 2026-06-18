<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestPrometheusMetricsSinkUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestPrometheusMetricsSinkUtil.java

Purpose: tests Prometheus metrics sink utility behavior for adding username/servername tags and normalizing metric names.

Important APIs/types/functions: `PrometheusMetricsSinkUtil.addTags`, `prometheusName`, `getMetricName`, `getUsername`, `MetricsTag`, username/servername tag constants, and representative metric record/name strings.

Control flow: tag tests call `addTags` with null, empty, and non-empty username plus UGI/non-UGI metric keys, then inspect returned tag lists for added or omitted tags. Naming tests feed camel-case, RocksDB, pipeline, and space-containing metric names into `prometheusName`, and helper tests check raw metric-name/username extraction when no embedded username exists.

State and persistence behavior: pure in-memory list/string transformations. Input tag lists are unmodifiable to ensure utility returns a usable copy rather than mutating immutable inputs.

Dependencies and integration points: feeds Prometheus exposition naming and labels used by `PrometheusMetricsSink` and HTTP metrics endpoints.

Risks: metric naming is dashboard/alert compatibility-sensitive. Tag-addition rules must avoid adding blank usernames and add servername only for UGI metrics.

Test signals: asserts absent username tag for null/empty username, present username tag for non-empty username, servername tag only for UGI metrics, both tags together, exact normalized names for camel-case/RocksDB/pipeline/space cases, unchanged metric name extraction, and null username extraction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestPrometheusMetricsSinkUtil.java -->
