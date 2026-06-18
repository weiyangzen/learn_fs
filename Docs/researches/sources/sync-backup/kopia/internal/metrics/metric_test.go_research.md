# sources/sync-backup/kopia/internal/metrics/metric_test.go

Purpose: provides a shared test helper for finding Prometheus metrics by name, type, and exact label set.

Important APIs/types/functions: `mustFindMetric`, `prometheus.DefaultGatherer.Gather`, `io_prometheus_client.MetricType`, and Prometheus metric families/labels.

Control flow: the helper gathers all registered metrics, scans for the desired family/type, then searches metric instances with the same label count and matching label values. On failure it logs all gathered metrics for diagnostics and fails the test.

State/persistence behavior: reads process-global Prometheus registry state. No durable state is used.

Dependencies/integration: used by counter, distribution, and throughput tests to verify Prometheus exporter integration in addition to Kopia snapshot state.

Risks/test signals: because it uses the default Prometheus gatherer, tests can be sensitive to global metric registration and name reuse across packages. Exact label matching avoids false positives among label variants.
