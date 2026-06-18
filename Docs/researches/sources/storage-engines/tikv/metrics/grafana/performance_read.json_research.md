# sources/storage-engines/tikv/metrics/grafana/performance_read.json

## Purpose

`sources/storage-engines/tikv/metrics/grafana/performance_read.json` is a Grafana dashboard definition titled `Test-Cluster-Performance-Read` with UID `4aVOvxcWk`. It is a read-workload performance dashboard for TiDB/TiKV test clusters. The file is declarative JSON, not executable application code: its behavioral surface is Grafana's dashboard schema, nested row panels, graph panels, templating variables, and Prometheus queries.

The dashboard is optimized for diagnosing read-path latency and saturation across TiDB SQL handling, TiDB transaction and TiKV client activity, PD TSO latency, TiKV gRPC work, TiKV storage read pools, coprocessor wait/handle behavior, RocksDB KV read efficiency, and node-level read disk I/O. The default time range is `now-6h` to `now`; `refresh` is `false`, so the dashboard does not auto-refresh unless a viewer changes the setting.

## Important APIs, Types, and Data Contracts

The primary API contract is Grafana dashboard schema version `18`, requiring Grafana `6.1.6`, the legacy `graph` panel plugin, and a Prometheus datasource input named `DS_TEST-CLUSTER` with label `test-cluster`. Every graph panel uses the datasource `${DS_TEST-CLUSTER}`.

The dashboard exposes two query template variables:

- `k8s_cluster`: Prometheus `label_values(tikv_engine_block_cache_size_bytes, k8s_cluster)`.
- `tidb_cluster`: Prometheus `label_values(tikv_engine_block_cache_size_bytes{k8s_cluster="$k8s_cluster"}, tidb_cluster)`.

Both variables are single-select (`multi=false`, `includeAll=false`) and are injected into almost every PromQL selector. This makes the dashboard strongly dependent on TiKV metrics that carry both `k8s_cluster` and `tidb_cluster` labels.

The file uses collapsed row panels as section containers. The top-level rows are:

- `TiDB-Server` with 4 graph children.
- `Parse` with 1 graph child.
- `Compile` with 1 graph child.
- `Transaction` with 3 graph children.
- `KV` with 5 graph children.
- `PD Client` with 2 graph children.
- `gRPC` with 2 graph children.
- `Storage` with 1 graph child.
- `Coprocessor` with 3 graph children.
- `RocksDB-KV` with 5 graph children.
- `Disk` with 4 graph children.

Important Prometheus metrics referenced by this dashboard include:

- TiDB server/session metrics: `tidb_server_handle_query_duration_seconds_bucket`, `tidb_server_get_token_duration_seconds_bucket`, `tidb_server_connections`, `go_memstats_heap_inuse_bytes`, `tidb_session_parse_duration_seconds_bucket`, `tidb_session_compile_duration_seconds_bucket`, `tidb_session_transaction_duration_seconds_bucket`, `tidb_session_transaction_statement_num_bucket`, and `tidb_session_retry_num_bucket`.
- TiDB TiKV client metrics: `tidb_tikvclient_txn_cmd_duration_seconds_bucket`, `tidb_tikvclient_lock_resolver_actions_total`, `tidb_tikvclient_backoff_seconds_bucket`, and `tidb_tikvclient_backoff_seconds_count`.
- PD client metrics: `pd_client_cmd_handle_cmds_duration_seconds_bucket` and `pd_client_request_handle_requests_duration_seconds_bucket` filtered to `type="tso"`.
- TiKV runtime and gRPC metrics: `tikv_grpc_msg_duration_seconds_bucket` and `tikv_thread_cpu_seconds_total`.
- TiKV coprocessor metrics: `tikv_coprocessor_request_wait_seconds_bucket` and `tikv_coprocessor_request_handle_seconds_bucket`.
- RocksDB/TiKV read metrics: `tikv_engine_get_micro_seconds`, `tikv_engine_memtable_efficiency`, `tikv_engine_cache_efficiency`, `tikv_engine_get_served`, `tikv_engine_seek_micro_seconds`, `tikv_engine_locate`, and `tikv_engine_bloom_efficiency`.
- Node exporter disk read metrics: `node_disk_read_time_seconds_total`, `node_disk_reads_completed_total`, and `node_disk_read_bytes_total`.

The graph panel contract uses Grafana fields such as `targets`, `legendFormat`, `xaxis`, `yaxes`, `tooltip`, `lines`, `linewidth`, `fill`, `nullPointMode`, and `gridPos`. Units include seconds (`s`), microseconds (`µs`), operations (`ops`), percent unit (`percentunit`), IOPS (`iops`), bytes, and bytes per second (`Bps`).

## Control Flow and Dashboard Layout

At load time, Grafana resolves the datasource input, evaluates the template variables, then renders only row headers initially because every top-level row has `collapsed=true`. When a row is expanded, Grafana renders the row's nested graph panels and executes their PromQL targets against `${DS_TEST-CLUSTER}`.

The read-path control flow is organized from front-end SQL service latency toward lower storage layers:

1. `TiDB-Server` panels show query duration quantiles (`0.999`, `0.99`, `0.95`, `0.80`), token acquisition latency, connection counts, and TiDB heap memory.
2. `Parse` and `Compile` show 99th percentile SQL parse and compile durations by `sql_type`.
3. `Transaction` shows transaction duration quantiles by `sql_type`, statement count quantiles, and retry count quantiles.
4. `KV` focuses on read commands by filtering `tidb_tikvclient_txn_cmd_duration_seconds_bucket` to `type=~"get|batch_get|seek|seek_reverse"`, plus lock resolver and backoff activity.
5. `PD Client` isolates TSO wait and RPC latency.
6. `gRPC` filters TiKV message duration to `type=~"kv_get|kv_batch_get|coprocessor"` and shows gRPC thread CPU.
7. `Storage` shows `store_read.*` thread CPU as a read-pool pressure signal.
8. `Coprocessor` shows request wait and handle quantiles plus `cop_.*` thread CPU.
9. `RocksDB-KV` shows get/seek microsecond summaries, operation distributions by level or cache path, cache hit ratios, and bloom-prefix efficiency.
10. `Disk` shows node-level read latency, operations, bandwidth, and load.

Most latency panels use `histogram_quantile()` over `sum(rate(..._bucket[1m])) by (le, ...)`; selected TiKV backoff and scheduler-style panels use a longer `[5m]` window to smooth sparse events. RocksDB get/seek duration panels use gauge-like summary metrics with `max(...)` across instances.

## State and Persistence Behavior

The file persists dashboard state as static JSON. Grafana stores the dashboard UID, title, panel IDs, collapsed row state, time picker options, default time window, and variable definitions. There is no runtime mutation in the repository source file; any changes made through the Grafana UI would need to be exported back to JSON to persist in source control.

The dashboard intentionally starts with all rows collapsed. This reduces initial query load but means users must expand sections to execute graph queries. Annotation support is enabled through the built-in `Annotations & Alerts` dashboard annotation with the same datasource, but the dashboard defines no custom links and no embedded alert rules in these graph panels.

Variable values are not persisted with concrete defaults: both variable `current` values are `null`. On import, Grafana must evaluate the Prometheus label queries before the dashboard becomes useful.

## Dependencies and Integration Points

The direct runtime dependencies are Grafana, the legacy graph panel, a Prometheus datasource, TiDB/TiKV metric exporters, PD client metrics, Go runtime metrics, and node exporter disk metrics. The dashboard also assumes a label taxonomy where TiDB, TiKV, PD-client, and node-exporter series all share `k8s_cluster` and `tidb_cluster`.

Integration points include:

- Grafana import/provisioning: the datasource input `DS_TEST-CLUSTER` must be mapped to a real Prometheus datasource.
- TiKV/TiDB monitoring stack: all referenced metrics must exist with compatible names and labels.
- Kubernetes labeling: `k8s_cluster` and `tidb_cluster` must be consistently populated across TiDB, TiKV, PD-client, and node-exporter series.
- Dashboard reconciliation tooling: top-level panels are rows with nested `panels`, so tooling that only scans `.panels[]` will miss all graph targets unless it traverses recursively.

## Risks and Edge Cases

The strongest correctness risk is in the `Block cache hit` panel's `all` target. It references `instance=~"$instance"` and `db="$db"`, but this dashboard defines only `k8s_cluster` and `tidb_cluster` variables. Unless Grafana receives `instance` and `db` from another provisioning layer, that query can evaluate with unresolved or empty template variables. The other block-cache targets hard-code `db="kv"` and do not depend on those missing variables.

The dashboard is versioned for Grafana `6.1.6` and legacy `graph` panels. Newer Grafana deployments may migrate graph panels to time-series panels, but migrations can change rendering defaults, legend behavior, and axis handling.

Because all rows are collapsed, health checks that only look at initial dashboard load may not exercise PromQL queries. Conversely, expanding many rows can generate a burst of Prometheus queries, especially histogram quantile panels over 1-minute windows.

The template variables are derived from `tikv_engine_block_cache_size_bytes`; if that metric is absent or missing labels, both selectors can fail even though many dashboard panels depend on unrelated TiDB or node metrics. This creates a hidden coupling between dashboard usability and block-cache metric availability.

Several panels use `max(...)` over TiKV microsecond metrics rather than grouping by instance. This highlights worst observed values but can hide which node contributed unless legend or query grouping is adjusted.

Disk panels filter only by cluster labels and not by device class. Environments with virtual, loop, or irrelevant devices can make disk latency/load graphs noisy unless Prometheus relabeling filters those devices upstream.

## Test Signals and Validation

Useful static validation signals:

- `jq` should parse the file successfully and confirm required top-level keys such as `__inputs`, `__requires`, `templating`, `panels`, `time`, `title`, and `uid`.
- Recursive panel traversal should find 11 collapsed top-level rows and 31 nested graph panels with Prometheus targets.
- Every graph panel should use `${DS_TEST-CLUSTER}` as datasource.
- Template variables should include exactly `k8s_cluster` and `tidb_cluster`; this also exposes the missing `$instance` and `$db` references in the block-cache `all` query.
- PromQL linting or Grafana query inspection should validate all metric names and label selectors against a representative TiDB/TiKV Prometheus.

Runtime validation should import the dashboard into a Grafana instance with a TiDB/TiKV Prometheus datasource, select a known test cluster, expand every row, and verify that each panel returns non-empty data during a read workload. The most important behavioral checks are read KV command duration, gRPC message duration for `kv_get`, coprocessor wait/handle latency, RocksDB get/seek duration, cache hit ratios, and node read disk I/O.
