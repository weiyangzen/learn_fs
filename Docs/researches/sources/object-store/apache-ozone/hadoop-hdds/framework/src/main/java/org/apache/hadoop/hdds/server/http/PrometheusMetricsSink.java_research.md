# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/PrometheusMetricsSink.java

Purpose: `PrometheusMetricsSink` is a Hadoop Metrics2 sink that caches counter/gauge metrics in Prometheus text exposition format for the `/prom` servlet.

Important APIs/types/functions: constructor stores a server name label. `putMetrics()` iterates metrics records, accepts counters and gauges, normalizes metric names through `PrometheusMetricsSinkUtil`, builds Prometheus sample keys with labels/tags, and stores values in `nextMetricLines`. `flush()` atomically swaps `nextMetricLines` into `metricLines`. `writeMetrics(Writer)` writes cached `# TYPE` lines and samples.

Control flow: Metrics2 calls `putMetrics()` repeatedly and then `flush()`. HTTP requests call `writeMetrics()` to stream the last flushed snapshot. Nested sorted synchronized maps keep deterministic output order.

State and persistence: in-memory snapshot maps only. No durable metrics history.

Dependencies/integration: registered by `BaseHttpServer.start()` when Prometheus support is enabled. Consumed by `PrometheusServlet`. Depends on Metrics2, Commons Configuration, and `PrometheusMetricsSinkUtil`.

Risks: label values are appended directly; correctness depends on upstream tag escaping/normalization. Only counters and gauges are exported; other metric types are ignored. The synchronized map plus method-level synchronization protects swaps, but the map values themselves are mutable synchronized maps.

Test signals: `TestPrometheusMetricsIntegration`, `TestPrometheusMetricsSinkUtil`, and volume IO Prometheus tests verify formatting, tag additions, name normalization, and integration output.
