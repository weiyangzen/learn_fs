# sources/storage-engines/foundationdb/fdbkubernetesmonitor/metrics.go

Purpose: defines custom Prometheus metrics for the Kubernetes monitor, tracking configuration changes, desired/running versions, process starts, and timestamps.

Important APIs and types: `metrics` holds counter/gauge vectors for restart count, configuration change count, last applied configuration timestamp, per-process start timestamp, running version, and desired version. `registerMetrics` creates and registers collectors. `registerConfigurationChange(version)` and `registerProcessStartup(processNumber, version)` update metric values.

Control flow: `monitor.startMonitor` registers metrics on a private registry, exposes `/metrics`, and stores the returned `metrics` object. `acceptConfiguration` calls `registerConfigurationChange`; `runProcess` calls `registerProcessStartup` after successful subprocess start.

State and persistence behavior: all state is in-memory Prometheus collector state. Previous desired/running version strings are tracked so old version gauges can be reset to zero when a different version appears.

Dependencies and integration points: depends on `prometheus/client_golang`. Metrics are consumed externally by Prometheus and by tests through registry gathering.

Risks: only a single previous running version is tracked globally, not per process, so mixed-version multi-process states may be simplified. GaugeVec label cardinality grows with observed versions until process lifetime ends.

Test signals: `metrics_test.go` verifies initial collectors, counter increments, desired/running version gauge resets, restart labels, and multi-process restart counter cardinality.
