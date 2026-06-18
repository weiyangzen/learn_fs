<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/prometheus.rules.yml -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/prometheus.rules.yml

Purpose: Prometheus recording rules that normalize raw Ganesha metrics for dashboards and alerting.

Important config surface: group `ganesha-rules` records RPC in-flight/completion/receive metrics, active-client estimates, NFS request rates, client request rates, per-export rates, byte throughput, request/response size histograms, NFS error rates and ratios, MDCACHE hit/miss ratios, wait time, and latency histogram rates. It computes percentiles for 1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, and 99 percentiles using `histogram_quantile`.

Control flow/state: Prometheus periodically evaluates expressions and persists resulting time series according to Prometheus retention. Labels intentionally drop `instance` and `job` for many aggregates and preserve operation/export/status dimensions depending on rule.

Dependencies/integration: required by `grafana.dashboard.json`, which queries the `ganesha:*` records. Depends on raw metrics such as `nfs_requests_total`, `client_requests_total`, `nfs_bytes_*`, `nfs_errors_total`, `mdcache_cache_*`, and `nfs_latency_ms_bucket`.

Risks: ratios can divide by zero and produce NaN/Inf during idle periods. Dropping `instance` and `job` aggregates multiple servers, which is useful globally but can hide per-instance faults. Histogram quantiles are only meaningful if bucket labels and metric cardinality are consistent.

Test signals: run `promtool check rules`, load alongside a Ganesha metrics endpoint, and verify Grafana panels resolve all `ganesha:*` queries without missing series.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/prometheus.rules.yml -->
