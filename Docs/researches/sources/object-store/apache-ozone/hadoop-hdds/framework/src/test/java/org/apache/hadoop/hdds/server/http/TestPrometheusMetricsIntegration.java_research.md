<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestPrometheusMetricsIntegration.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestPrometheusMetricsIntegration.java

Purpose: integration tests for `PrometheusMetricsSink` with Hadoop Metrics2 publication, covering metric formatting, duplicate metric names with labels, HELP/TYPE uniqueness, and stale metric removal across flushes.

Important APIs/types/functions: `DefaultMetricsSystem.instance`, `MetricsSystem.register`, `unregisterSource`, `publishMetricsNow`, `PrometheusMetricsSink.writeMetrics`, `MetricsSource`, `MetricsCollector`, `MetricsTag`, `MutableCounterLong`, `@Metrics`, `@Metric`, and `GenericTestUtils.waitFor`.

Control flow: setup registers a Prometheus sink with the default metrics system; teardown stops it. Tests register annotated or lambda metrics sources, mutate counters, wait until expected metric names appear in sink output, and assert Prometheus text contains expected samples and metadata. Stale-metric testing unregisters one source, registers another, republishes, and verifies old samples disappear.

State and persistence behavior: metrics system state is global in-process and reset by teardown. Sink output is written to an in-memory writer. Stale samples are held inside the sink until flush/publish cycles.

Dependencies and integration points: integrates Metrics2 with Prometheus exposition formatting, Apache Commons string counting, and Ozone sink naming/tag utilities.

Risks: default metrics system global state can leak between tests if teardown fails. Asynchronous metrics publication requires polling. Formatting assertions are sensitive to name-normalization changes.

Test signals: asserts exported counter samples with labels, duplicate metric names disambiguated by labels, single TYPE line for same metric with different labels, stale metric removal after source replacement, and expected HELP/TYPE/sample content.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestPrometheusMetricsIntegration.java -->
