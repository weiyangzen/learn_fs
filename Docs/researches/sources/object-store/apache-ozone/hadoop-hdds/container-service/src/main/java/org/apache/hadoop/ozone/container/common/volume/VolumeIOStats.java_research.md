# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeIOStats.java

Purpose: Per-HDDS-volume metrics source for read/write bytes, operation counts, latencies, and latency quantiles.

Important APIs and types: Constructor names the metrics source by identifier and optionally creates quantiles from configured intervals. Increment methods update bytes, op counts, and read/write timings; `recordReadOperation` combines elapsed time, op count, and bytes. Getter methods expose counter/rate values and `getStorageDirectory` is annotated as a metric.

Control flow: Construction sets quantile arrays when intervals are configured and registers with the default metrics system. `HddsVolume` creates and unregisters it for normal data volumes.

State and persistence: Runtime metrics only. No on-disk persistence.

Dependencies and integration points: Uses Metrics2 mutable counters, rates, and quantiles. `HddsVolume.getVolumeIOStats` exposes it to container IO code.

Risks: If no percentile intervals are configured, `readLatencyQuantiles` and `writeLatencyQuantiles` may remain null, but `incReadTime` and `incWriteTime` iterate them unconditionally. Tests should cover empty/null interval behavior, registration/unregistration, and counter updates through both direct increments and convenience methods.
