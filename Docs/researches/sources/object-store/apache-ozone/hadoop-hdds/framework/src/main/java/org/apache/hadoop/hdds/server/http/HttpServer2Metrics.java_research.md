# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/HttpServer2Metrics.java

Purpose: `HttpServer2Metrics` exposes Jetty queued thread pool state through Hadoop Metrics2.

Important APIs/types/functions: `create(QueuedThreadPool, name)` registers a metrics source named `HttpServer2Metrics`. `getMetrics()` emits gauges for total threads, idle threads, max threads, and queued waiting tasks, tagged with server name. `unRegister()` unregisters the source. The nested `HttpServer2MetricsInfo` enum supplies Metrics2 names/descriptions.

Control flow: `HttpServer2.initializeWebServer()` creates this metrics source after configuring the Jetty thread pool. `HttpServer2.stop()` calls `unRegister()`.

State and persistence: stores a reference to the live Jetty `QueuedThreadPool` and server name. Metrics are sampled live; no durable state.

Dependencies/integration: depends on Jetty `QueuedThreadPool`, Hadoop Metrics2, and `DefaultMetricsSystem`. Exportable through the Prometheus sink once Metrics2 emits records.

Risks: `SOURCE_NAME`/`NAME` are static, so multiple simultaneous `HttpServer2` instances can conflict in the metrics system. The server name tag disambiguates records but not source registration.

Test signals: `TestHttpServer2Metrics` mocks a collector and thread pool to verify record name, tag, and gauge values.
