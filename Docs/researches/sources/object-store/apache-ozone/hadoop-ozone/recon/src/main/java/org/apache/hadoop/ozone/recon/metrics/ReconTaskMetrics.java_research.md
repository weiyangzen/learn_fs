## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconTaskMetrics.java

Purpose: dynamic per-task Metrics2 source for delta processing and reprocess timings/failures.

Important APIs/types/functions: static `create`; `unRegister`; increment/update methods for task delta success/failure/duration and task reprocess failure/duration; getters; `getMetrics`; `sanitizeTaskName`.

Control flow: metric objects are lazily created in concurrent maps per task name using a `MetricsRegistry`. `getMetrics` snapshots the static task counter and all dynamic counters/rates.

State and persistence: in-memory concurrent maps of metric objects; no DB writes. Integrates with Recon task framework and Metrics2.

Risks: `numTasksTracked` is declared but not incremented when new task metrics are created, so it may not reflect unique tasks. Sanitization can collide different task names. Tests should cover lazy creation, name sanitization/collisions, metric snapshots, concurrency, and expected value for `numTasksTracked`.
