<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/MetricsSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/MetricsSubCommand.java

Purpose: picocli `metrics`/`metric` subcommand that fetches Prometheus metrics for a selected insight point and prints selected values.

Important APIs: option `-f` supplies filters, parameter `insightName` selects an insight. `call()` resolves the insight, computes unique source components from metric groups, downloads `/prom` per component, and prints each group and metric value. `getMetrics(conf, component)` opens `<host>/prom` via `InsightHttpUtils`, reads the response, and splits into lines. `selectValue` scans lines for a metric id prefix and required `key="value"` tags, returning the second whitespace token or `???`.

Control flow and integration: metric descriptors are metadata only; this command implements matching. It integrates with Ozone's Prometheus endpoint and the common HTTP/SPNEGO helper.

State and persistence: no persistent state. Runtime state is the downloaded metrics map.

Risks and tests: `startsWith(metricId)` may match longer metric names sharing the same prefix. Value parsing assumes Prometheus sample lines have at least two space-separated tokens and ignores timestamps. It calls `insight.getMetrics(filters)` twice, which can repeat expensive work for datanode/pipeline insights if metrics become dynamic. No direct tests exercise `/prom` parsing or missing metric behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/MetricsSubCommand.java -->
