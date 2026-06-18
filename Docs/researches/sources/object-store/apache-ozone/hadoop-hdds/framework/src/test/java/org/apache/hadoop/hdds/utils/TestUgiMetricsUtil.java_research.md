<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestUgiMetricsUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestUgiMetricsUtil.java

Purpose: tests `UgiMetricsUtil.createServernameTag`, which adds a servername metrics tag only for compatible UGI metrics keys.

Important APIs/types/functions: `UgiMetricsUtil.createServernameTag`, `Optional<MetricsTag>`, Hadoop `MetricsTag`, compatible key `ugi_metrics`, and non-compatible key handling.

Control flow: one test passes a non-UGI key and asserts no tag is returned. The other passes `ugi_metrics` plus a server name and asserts a present tag with expected value, name, and description.

State and persistence behavior: pure in-memory key/tag creation; no external state or persistence.

Dependencies and integration points: supports Prometheus/Metrics2 labeling by adding server identity to UGI metrics before export.

Risks: compatibility depends on matching the UGI metrics key convention exactly. If the metrics key changes, servername labeling can silently disappear.

Test signals: asserts absent tag for non-compatible keys and present tag with value/name `servername` and description `name of the server` for `ugi_metrics`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestUgiMetricsUtil.java -->
