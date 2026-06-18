# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/CpuMetrics.java

Purpose: `CpuMetrics` exposes JVM process CPU load, system CPU load, and available processors through Hadoop Metrics2.

Important APIs/types/functions: constructor captures `com.sun.management.OperatingSystemMXBean`. Static `create()` registers a source named `JvmMetricsCpu` only if one is not already present. `getMetrics()` adds gauges `jvmLoad`, `systemLoad`, and `availableProcessors`.

Control flow: services call `CpuMetrics.create()` during metrics initialization. Metrics2 later invokes `getMetrics()` to sample live MXBean values.

State and persistence: holds an MXBean reference; no persistence. Metrics values are live samples.

Dependencies/integration: depends on `ManagementFactory`, `OperatingSystemMXBean`, Hadoop Metrics2, `DefaultMetricsSystem`, and Ozone metrics context constants. Exportable via Prometheus sink.

Risks: `com.sun.management.OperatingSystemMXBean` is a JDK-specific extension; alternate JVMs may behave differently. CPU load methods can return negative values if unavailable depending on JVM implementation.

Test signals: integration test class `TestCpuMetrics` verifies CPU metrics availability through the Ozone metrics path.
