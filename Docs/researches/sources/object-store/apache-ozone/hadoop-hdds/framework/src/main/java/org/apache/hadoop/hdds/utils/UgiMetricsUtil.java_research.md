# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/UgiMetricsUtil.java

## Purpose
`UgiMetricsUtil` adds Ozone-specific servername tagging for Hadoop UGI metrics so Prometheus output can distinguish the server associated with user/group metrics.

## Important APIs and Types
`createServernameTag(String key, String servername)` returns `Optional.empty()` unless the metric key contains `ugi_metrics`; otherwise it creates a `MetricsTag` whose info name is `servername` and value is the supplied server name.

## Control Flow and State
The class is stateless. It performs a substring check on the metric key and constructs an inline `MetricsInfo` instance when a tag is needed.

## Persistence, Dependencies, and Integration
No persistence exists. Dependencies are Hadoop `MetricsInfo` and `MetricsTag`. `PrometheusMetricsSinkUtil.addTags` calls this helper while adapting metrics records for Prometheus.

## Risks and Test Signals
The substring match is broad; unrelated keys containing `ugi_metrics` will be tagged. Null keys would throw. Tests should cover matching and non-matching keys, null/empty server names if allowed by callers, metrics info name/description, and integration with `PrometheusMetricsSinkUtil.addTags`.
