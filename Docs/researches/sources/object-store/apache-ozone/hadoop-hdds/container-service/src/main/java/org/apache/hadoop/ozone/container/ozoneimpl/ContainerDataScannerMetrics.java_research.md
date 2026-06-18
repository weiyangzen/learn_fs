## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerDataScannerMetrics.java

Purpose: Metrics source for per-volume background container data scanners.

Important APIs and functions: `create(volumeName)` registers a uniquely named Metrics2 source. `incNumBytesScanned()` records scanner bandwidth through a `MutableRate`. Mean, sample count, and standard deviation getters expose scan bandwidth statistics. `getStorageDirectory()` and `setStorageDirectory()` publish the scanned volume directory.

Control flow and state: Extends the shared scanner metrics base. Empty volume names receive a random suffix to avoid duplicate metrics names. Colons in volume names are replaced for metric source naming.

Persistence and dependencies: In-memory telemetry only. Depends on `DefaultMetricsSystem`, `MutableRate`, and thread-local random for fallback names.

Risks: Volume path-based names can still collide after character replacement. `ThreadLocalRandom` fallback makes names non-deterministic for empty volume names. Rate statistics reflect throttler calls, not necessarily verified bytes.

Test signals: Metrics registration by volume name, empty-name fallback, byte rate updates, storage directory metric, inherited container/unhealthy/iteration counters, and unregister during scanner shutdown.
