# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/ContainerClientMetrics.java

Purpose: Hadoop metrics source for container client write distribution and latency measurements.

Important APIs/types/functions: Static `acquire`, `acquireHandle`, and `release` manage a singleton metrics source with reference counting. `Handle` is `AutoCloseable`. Counters track total write-chunk calls/bytes, per-pipeline calls/bytes, and leader call counts. Mutable rates track hsync phases. Quantile arrays cover list/get/read/get-small-file/hsync latencies for 60/300/900 second intervals.

Control flow: First acquire registers an instance with `DefaultMetricsSystem` under a unique source name. Each acquire increments `referenceCount`. Release decrements and unregisters/stops quantiles when the count reaches zero. `recordWriteChunk` lazily creates per-pipeline/per-leader counters and increments totals. Latency methods add samples to every configured quantile.

State and persistence behavior: Static singleton, reference count, instance count, metrics registry, concurrent maps, and mutable metric objects. Metrics are process-local and exported through Hadoop metrics, not persisted by this class.

Dependencies and integration points: Used by write paths to report container IO. Depends on Hadoop metrics2, `Pipeline`, `PipelineID`, `DatanodeID`, and `MetricUtil`.

Risks: Manual reference counting can leak metrics if clients do not release, or throw if release is called too often. Dynamic metric names include IDs and can grow with many pipelines. Singleton synchronization protects acquire/release but per-metric maps rely on concurrent structures.

Test signals: Tests should cover acquire/release lifecycle, handle idempotent close, per-pipeline counter creation, quantile stopping, and reference-count edge cases.
