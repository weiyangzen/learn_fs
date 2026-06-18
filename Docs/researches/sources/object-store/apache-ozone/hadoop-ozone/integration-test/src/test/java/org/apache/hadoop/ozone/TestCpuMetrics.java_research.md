# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestCpuMetrics.java

Purpose: abstract non-HA integration test that verifies SCM Prometheus metrics endpoint exposes JVM CPU metrics.

Important APIs/types/functions: `TestCpuMetrics` implements `NonHATests.TestCase`, has an `OkHttpClient`, and one test method `testCpuMetrics`. It uses `cluster()` from the test-case interface, `HddsUtils.getPortNumberFromConfigKeys`, `OZONE_SCM_HTTP_ADDRESS_KEY`, OkHttp `Request`/`Response`, and AssertJ.

Control flow: it builds `http://localhost:<scm-http-port>/prom` from cluster configuration, performs an HTTP GET, reads the response body as a string, and asserts the body contains `jvm_metrics_cpu_available_processors`, `jvm_metrics_cpu_system_load`, and `jvm_metrics_cpu_jvm_load`.

State and persistence: no own persistence. It observes the running SCM HTTP server and metrics registry exposed by the non-HA test cluster.

Dependencies and integration points: SCM HTTP endpoint, Prometheus metrics servlet, JVM metrics source, OkHttp, and the non-HA test harness that supplies the cluster.

Risks: assumes the SCM HTTP address resolves to localhost and the port is present in config. It does not assert HTTP status code or close the response explicitly beyond reading the body, relying on OkHttp cleanup. Metric names are exact string checks and will fail on metrics rename/export format changes.

Test signals: non-null response body and presence of three CPU metric names in `/prom` output.
