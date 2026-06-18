## sources/user-network-fs/gcsfuse/internal/monitor/otelexporters.go

### Purpose
`otelexporters.go` configures OpenTelemetry metric export for gcsfuse, including Prometheus scraping, Google Cloud Monitoring export, metric filtering, resource attribution, and exporter shutdown joining.

### Important APIs, Types, And Functions
`SetupOTelMetricExporters` is the main entry point. Helpers include `dropDisallowedMetricsView`, `setupCloudMonitoring`, `metricFormatter`, `setupPrometheus`, `serveMetrics`, and `getResource`. `permissionAwareExporter` wraps an OTel metric exporter and disables itself after Cloud Monitoring permission-denied errors.

### Control Flow
Setup collects metric provider options from Prometheus and Cloud Monitoring configuration, attempts to detect/build a GCP resource with service name/version/instance ID, adds a view that drops disallowed metric prefixes, disables exemplars, creates and installs a global meter provider, and returns a joined shutdown function. Prometheus starts an HTTP server on `/metrics` and waits on a shutdown channel. Cloud Monitoring creates a periodic reader when interval seconds are positive.

### State, Persistence, And Dependencies
State includes the global OTel meter provider, the Prometheus server goroutines, and `permissionAwareExporter.disabled`. Persistent output is external: Prometheus HTTP endpoint and Cloud Monitoring custom metrics with prefix `custom.googleapis.com/gcsfuse/`. Dependencies include OTel SDK, GCP resource detector, Google Cloud metric exporter, Prometheus exporter/client, gRPC status codes, and common shutdown utilities.

### Integration Points
Metrics emitted by `metrics` package instruments and the monitoring bucket flow through this provider. Resource attributes connect metrics to mount ID and gcsfuse version.

### Risks
Global OTel provider replacement can affect tests or multiple mounts in one process. `setupPrometheus` uses an unbuffered shutdown channel; callers must invoke shutdown at most once. The metric filtering view silently drops instruments outside hard-coded prefixes. PermissionDenied disables Cloud Monitoring after the first such export, but the first call still returns the original error.

### Test Signals
`otelexporters_test.go` covers `permissionAwareExporter` success, PermissionDenied disable/skip, and non-permission error behavior. Prometheus serving, resource detection, metric prefix filtering, and Cloud Monitoring reader creation are not directly tested.
