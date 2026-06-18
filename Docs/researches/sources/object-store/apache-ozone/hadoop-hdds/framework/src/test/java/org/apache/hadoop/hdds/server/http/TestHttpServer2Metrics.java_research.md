<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHttpServer2Metrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHttpServer2Metrics.java

Purpose: tests that `HttpServer2Metrics` exports Jetty thread-pool gauges and server-name tags to Hadoop Metrics2.

Important APIs/types/functions: `HttpServer2Metrics.create`, `getMetrics`, `QueuedThreadPool`, `MetricsCollector`, `MetricsRecordBuilder`, metrics infos `HttpServerThreadCount`, `HttpServerMaxThreadCount`, `HttpServerIdleThreadCount`, `HttpServerThreadQueueWaitingTaskCount`, and `SERVER_NAME`.

Control flow: mocks a `QueuedThreadPool` and Metrics2 collector/record builder, stubs thread counts and queue size, creates the metrics source, invokes `getMetrics`, and verifies record creation, context/tagging, and gauge values.

State and persistence behavior: no persistent state. Metrics values are read from mocks and passed to Metrics2 mocks.

Dependencies and integration points: integrates Jetty threading metrics with Hadoop Metrics2 source/collector contracts and Mockito verification.

Risks: verifies exact metric names and gauges; any intentional metric rename requires test updates. It does not register with a live metrics system.

Test signals: verifies source record name, server-name tag, and all four gauge values are emitted.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHttpServer2Metrics.java -->
