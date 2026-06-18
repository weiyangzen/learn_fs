<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/grafana.dashboard.json -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/grafana.dashboard.json

Purpose: sample Grafana dashboard for a local NFS-Ganesha Prometheus deployment. It is schemaVersion 27, uses datasource `Prometheus`, and has dashboard title `Ganesha (local)`.

Important API/config surface: the visible top-level panels include summary rows plus request rate, 50th percentile latency, throughput, and metadata cache hit ratio graphs. The dashboard also carries nested row panels for latency percentiles, request/response size heatmaps, errors, per-export metrics, per-export latency, RPCs in flight, RPC receive/complete rates, and active clients.

Control flow/state: no runtime logic or persistence beyond Grafana dashboard JSON. The dashboard depends on Grafana loading the JSON and evaluating PromQL queries such as `ganesha:nfs_requests:rate1m`, `ganesha:latency_ms_percentile:rate1m`, `ganesha:nfs_bytes_transferred:rate1m`, and `ganesha:mdcache_cache_hit_ratio:rate1m`.

Dependencies/integration: tightly coupled to `prometheus.rules.yml`, which defines the `ganesha:*` recording rules and percentile labels the dashboard queries. It assumes NFS-Ganesha exports Prometheus metrics for RPCs, NFS operations, bytes, errors, MDCACHE, latency buckets, and per-export variants.

Risks: the dashboard uses older Grafana graph/row structure with nested panels, so migration to newer Grafana may flatten or reinterpret rows. The empty `uid`, no templating variables, and fixed datasource name make it less portable. Panels silently fail if recording rules are not installed.

Test signals: import the JSON into Grafana with the Prometheus datasource named `Prometheus`, load `prometheus.rules.yml`, and confirm the 30 query-bearing panels render non-empty series under Ganesha load.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/grafana.dashboard.json -->
