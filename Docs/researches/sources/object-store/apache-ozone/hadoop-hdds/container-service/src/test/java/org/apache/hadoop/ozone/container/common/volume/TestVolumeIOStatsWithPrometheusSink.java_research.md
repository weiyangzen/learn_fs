# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestVolumeIOStatsWithPrometheusSink.java

## Purpose
Verifies multiple `VolumeIOStats` sources are exported through `PrometheusMetricsSink` with distinct `storagedirectory` labels.

## Important APIs, Types, And Functions
Uses `DefaultMetricsSystem`, `PrometheusMetricsSink.writeMetrics`, `VolumeIOStats`, and IO percentile interval configuration.

## Control Flow
Setup initializes the metrics system and registers the sink. The test creates two stats sources, publishes metrics, writes Prometheus output to memory, and asserts both storage directory labels are present. Teardown stops metrics.

## State And Persistence
Metrics registration is process-global state. Output is in-memory text.

## Dependencies And Integration Points
Integrates Hadoop metrics2, Ozone Prometheus sink, and volume IO metrics source labels.

## Risks And Edge Cases
Global metrics state can interfere with other tests if teardown fails. The test checks label presence, not metric values.

## Test Signals
Prometheus output contains both `storagedirectory` label values.
