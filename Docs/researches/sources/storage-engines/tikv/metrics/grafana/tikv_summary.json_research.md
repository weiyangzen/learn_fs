# sources/storage-engines/tikv/metrics/grafana/tikv_summary.json

## Purpose

`tikv_summary.json` is a Grafana dashboard definition for the `Test-Cluster-TiKV-Summary` dashboard. It is not executable TiKV code; it is an operational monitoring artifact that encodes the Prometheus queries, Grafana panels, dashboard variables, units, thresholds, and legacy Grafana alerts used to summarize TiKV cluster health. The dashboard defaults to a rolling `now-5m` to `now` window, refreshes every minute, uses browser timezone rendering, and targets a Prometheus datasource input named `DS_TEST-CLUSTER`.

The dashboard is source-tree-aligned with TiKV metrics because its PromQL depends directly on TiKV-exported metric names and labels. It gives operators a compact view of capacity, resource usage, request throughput, error rates, Raft leadership/region counts, storage engine behavior, gRPC latency, internal thread-pool CPU consumption, and PD communication.

## Dashboard Contract and Important Configuration Objects

- Dashboard metadata: title `Test-Cluster-TiKV-Summary`, uid `X7VQmEzZk`, schemaVersion `18`, Grafana requirement `6.1.6`, Prometheus datasource requirement `1.0.0`, graph panel requirement, dark style, editable set to true.
- Datasource input: `DS_TEST-CLUSTER`, labeled `test-cluster`, is the only declared input and is used by templating variables and annotation configuration.
- Templating variables:
  - `k8s_cluster`: hidden query variable from `label_values(tikv_engine_block_cache_size_bytes, k8s_cluster)`.
  - `tidb_cluster`: hidden query variable constrained by selected `k8s_cluster`.
  - `db`: visible multi-select/all variable from `tikv_engine_block_cache_size_bytes`, filtered by `k8s_cluster` and `tidb_cluster`. This dashboard does not use `$db` in panel PromQL, so it is effectively unused here.
  - `command`: visible multi-select/all variable from `tikv_storage_command_total` label `type`. This dashboard also does not use `$command` in panel PromQL.
  - `instance`: visible instance selector from `tikv_engine_size_bytes`, filtered by `k8s_cluster` and `tidb_cluster`, used throughout panel queries as `instance=~"$instance"`.
- Annotation configuration: built-in dashboard annotations are enabled but hidden, using the same datasource input.
- Timepicker: exposes short operational windows from `5m` through `30d` and refresh intervals from `5s` through `1d`.

There are 48 dashboard/panel objects: 6 row panels and 42 graph panels. The rows are `Cluster`, `Errors`, `Server`, `gRPC`, `Thread CPU`, and `PD`.

## Panel Groups and Query Behavior

### Cluster

The `Cluster` row contains the high-level TiKV health panels:

- `Store size`, `Available size`, and `Capacity size` query `tikv_store_size_bytes` for `type="used"`, `type="available"`, and `type="capacity"` by `instance`. These panels are stacked and rendered in decimal bytes.
- `CPU` combines `rate(process_cpu_seconds_total{job="tikv"}[1m])` by instance with `tikv_server_cpu_cores_quota`, so it compares observed process CPU use against server CPU quota.
- `Memory` combines `process_resident_memory_bytes` by instance with `tikv_server_memory_quota_bytes`.
- `IO utilization` reads `rate(node_disk_io_time_seconds_total[1m])` and legends by instance/device. It depends on node exporter style disk metrics carrying the same cluster labels.
- `MBps` derives RocksDB/engine write throughput from `tikv_engine_flow_bytes{db="kv", type="wal_file_bytes"}` and read throughput from `type=~"bytes_read|iter_bytes_read"`.
- `QPS` uses `tikv_grpc_msg_duration_seconds_count` by instance/type, excluding `kv_gc`.
- `Errps` combines gRPC failures, missing/noop PD heartbeat detection via `delta(tikv_pd_heartbeat_message_total{type="noop"}[1m]) < 1`, and critical errors.
- `Leader` and `Region` summarize `tikv_raftstore_region_count` for leader and region counts; the leader panel also includes a negative leader-drop expression using `delta(...[30s]) < -10`.

### Errors

The `Errors` row focuses on conditions that should normally stay at zero:

- `Critical error`: rate of `tikv_critical_error_total` by instance/type, with a legacy alert when average value is greater than zero.
- `Server is busy`: combines scheduler-too-busy, channel-full, coprocessor `type='full'` errors, and `tikv_engine_write_stall{type="write_stall_percentile99"}`.
- `Server report failures`: rate of `tikv_server_report_failure_msg_total` by type/instance/store_id, with a legacy alert on any positive max.
- `Raftstore error`: filters `tikv_storage_engine_async_request_total` to non-success/non-all statuses.
- `Scheduler error`: filters `tikv_scheduler_stage_total` to `snapshot_err|prepare_write_err`.
- `Coprocessor error`: rate of `tikv_coprocessor_request_error` by reason.
- `gRPC message error`: rate of `tikv_grpc_msg_fail_total` by message type.
- `Leader drop`: one-minute delta of leader region count.
- `Leader missing`: current `tikv_raftstore_leader_missing` by instance.

Several panels use `null as zero` and hide empty/zero series, which makes sparse error metrics easier to scan but can hide scrape gaps if the datasource also has missing samples.

### Server

The `Server` row ties capacity and storage-engine behavior to store-level limits:

- `CF size`: `tikv_engine_size_bytes` by `type`, stacked in decimal bytes.
- `Store size`: repeated store-used view from `tikv_store_size_bytes{type="used"}` by instance.
- `Channel full`: rate of `tikv_channel_full_total` by instance/type, with a legacy alert when average value is positive.
- `Approximate Region size`: 99th percentile, 95th percentile, and average from `tikv_raftstore_region_size_bucket`, `_sum`, and `_count`. It has a legacy alert when the 99th percentile exceeds `1073741824` bytes.

### gRPC

The `gRPC` row monitors RPC traffic shape and latency:

- `gRPC message count`: request rate from `tikv_grpc_msg_duration_seconds_count` by type, excluding `kv_gc`.
- `gRPC message failed`: failure rate from `tikv_grpc_msg_fail_total` by type, excluding `kv_gc`.
- `99% gRPC message duration`: `histogram_quantile(0.99, sum(rate(tikv_grpc_msg_duration_seconds_bucket[1m])) by (le, type))`.
- `Average gRPC message duration`: sum/count ratio from `tikv_grpc_msg_duration_seconds_sum` and `_count` by type.

The p99 duration panel uses a log-base-10 seconds axis, while the average duration panel uses a log-base-2 seconds axis. That difference is visual-only but can affect operator interpretation when comparing the two.

### Thread CPU

The `Thread CPU` row maps TiKV thread-name conventions to internal subsystem CPU use, all via `rate(tikv_thread_cpu_seconds_total[1m])` grouped by instance:

- `Raft store CPU`: `name=~"(raftstore|rs)_.*"`, alert threshold greater than `1.7`.
- `Async apply CPU`: `name=~"apply_[0-9]+"`, alert threshold greater than `1.8`.
- `Scheduler worker CPU`: `name=~"sched_.*"`, alert threshold greater than `3.6`.
- `gRPC poll CPU`: `name=~"grpc.*"`, alert threshold greater than `3.6`.
- `Coprocessor CPU`: separate normal/high/low expressions for `cop_normal.*`, `cop_high.*`, and `cop_low.*`; the embedded alert checks query A only, so it alerts on normal coprocessor CPU rather than the combined three-class total.
- `Storage ReadPool CPU`: separate normal/high/low expressions for `store_read_norm.*`, `store_read_high.*`, and `store_read_low.*`; the embedded alert checks query A only, so it alerts on normal read-pool CPU.
- `Split check CPU`: `name=~"split_check"`.
- `RocksDB CPU`: `name=~"rocksdb.*"`, with visual warning threshold above `1` and critical threshold above `4` but no legacy alert.
- `GC worker CPU`: `name=~"gc_worker.*"`.
- `Snapshot worker CPU`: `name=~"snapshot_worker"`.

These panels depend heavily on TiKV thread naming stability. Renaming thread pools or changing label cardinality will silently change dashboard semantics.

### PD

The `PD` row observes TiKV-to-PD interaction:

- `PD requests`: rate of `tikv_pd_request_duration_seconds_count` by request type.
- `PD request duration (average)`: sum/count ratio from `tikv_pd_request_duration_seconds_sum` and `_count`.
- `PD heartbeats`: rate of `tikv_pd_heartbeat_message_total` by type.
- `PD validate peers`: rate of `tikv_pd_validate_peer_total` by type.

These panels are integration health signals: they do not directly inspect PD internals, but they expose what TiKV reports about its PD request path and heartbeat/peer-validation behavior.

## Metrics and Dependencies

The dashboard directly references these TiKV metric families:

`tikv_channel_full_total`, `tikv_coprocessor_request_error`, `tikv_critical_error_total`, `tikv_engine_flow_bytes`, `tikv_engine_size_bytes`, `tikv_engine_write_stall`, `tikv_grpc_msg_duration_seconds_bucket`, `tikv_grpc_msg_duration_seconds_count`, `tikv_grpc_msg_duration_seconds_sum`, `tikv_grpc_msg_fail_total`, `tikv_pd_heartbeat_message_total`, `tikv_pd_request_duration_seconds_count`, `tikv_pd_request_duration_seconds_sum`, `tikv_pd_validate_peer_total`, `tikv_raftstore_leader_missing`, `tikv_raftstore_region_count`, `tikv_raftstore_region_size_bucket`, `tikv_raftstore_region_size_count`, `tikv_raftstore_region_size_sum`, `tikv_scheduler_stage_total`, `tikv_scheduler_too_busy_total`, `tikv_server_cpu_cores_quota`, `tikv_server_memory_quota_bytes`, `tikv_server_report_failure_msg_total`, `tikv_storage_engine_async_request_total`, `tikv_store_size_bytes`, and `tikv_thread_cpu_seconds_total`.

It also depends on non-TiKV exporter metrics:

- `process_cpu_seconds_total` and `process_resident_memory_bytes` from process/runtime exporters.
- `node_disk_io_time_seconds_total` from node exporter or an equivalent disk metrics source.

The common label contract is `k8s_cluster`, `tidb_cluster`, and usually `instance`. Some panels also require `job`, `type`, `db`, `name`, `stage`, `status`, `store_id`, `reason`, `device`, and histogram `le`. The dashboard assumes these labels are present and consistently propagated across TiKV, process, and node exporter metrics.

## Control Flow

At import time, Grafana binds `${DS_TEST-CLUSTER}` to a Prometheus datasource. On page load, Grafana evaluates template variables in dependency order: `k8s_cluster`, then `tidb_cluster`, then visible `db`, `command`, and `instance`. Panel PromQL uses the selected cluster labels and instance regex to generate time-series queries over the dashboard time range. Most rates use a fixed `[1m]` window, independent of the visible dashboard range.

Rows group panels but do not transform data. Each graph panel independently evaluates its targets. Histogram panels use `histogram_quantile` after summing rates by `le` and sometimes by request `type`; average latency/size panels divide `_sum` rates by `_count` rates. Legacy alert definitions are embedded in selected panels and evaluate specific query refs over short windows such as `10s`, `1m`, or `5m`.

## State and Persistence Behavior

The dashboard JSON is persistent configuration. Runtime metric state is external to this file and lives in Prometheus/remote storage. Grafana stores view state, selected variables, panel rendering state, annotations, and alert evaluation state outside this file after import.

The file contains stable identifiers such as dashboard `uid`, panel ids, version `5`, iteration timestamp `1566459338986`, and grid positions. It has `id: null` and `gnetId: null`, so it is intended to be imported into a Grafana instance rather than tied to one existing Grafana database row. Because `editable` is true, operators can mutate the dashboard in Grafana; those mutations only persist back to source control if exported and committed.

## Integration Points

- TiKV instrumentation must emit the metric names and labels referenced above.
- Prometheus scrape configuration must collect TiKV, process, and node exporter metrics and retain the `k8s_cluster`/`tidb_cluster` labels expected by every query.
- Grafana must support legacy graph panels and legacy panel alert JSON. The declared Grafana version is `6.1.6`, so migration to newer Grafana releases may require panel or alert conversion.
- TiDB/TiKV deployment metadata must make `k8s_cluster`, `tidb_cluster`, and `instance` meaningful. The hidden cluster variables make the dashboard easy to embed for a fixed environment but less transparent if imports happen without defaults.
- PD integration is observed through TiKV-exported PD request and heartbeat metrics, not through direct PD datasource queries.

## Risks and Maintenance Notes

- Metric or label drift is the largest risk. Any rename of TiKV metric families, thread-name labels, histogram suffixes, or cluster labels will produce empty or misleading panels.
- `$db` and `$command` are defined but unused in panel PromQL. They may be leftover from a broader dashboard and can confuse operators who expect them to filter data.
- The CPU panels use `percentunit` axes while plotting raw CPU-second rates. Values can exceed `1.0` for multi-core thread pools, and alert thresholds such as `3.6` depend on this multi-core interpretation.
- Some alerts only check query ref `A` even when panels contain multiple subsystem queries. This matters for `Coprocessor CPU` and `Storage ReadPool CPU`, where high/low pools are displayed but not included in the embedded alert condition.
- `node_disk_io_time_seconds_total` has no `instance=~"$instance"` filter in its query, so the IO utilization panel can include disks from all nodes in the selected clusters if the node exporter label model does not line up with TiKV instances.
- Legacy alert definitions include `datasourceId: 1` in some embedded models, which can become wrong after import into another Grafana database.
- Several error panels use `null as zero`; this is convenient for sparse counters but can mask scrape absence if paired with permissive no-data alert behavior.
- Fixed `[1m]` PromQL windows can be noisy for low-traffic clusters and can under-smooth during incident response. They also assume scrape intervals are short enough to make one-minute rates reliable.

## Test Signals

Useful validation for changes to this file:

- Parse the file with `jq` or Grafana provisioning import to catch invalid JSON/schema regressions.
- Confirm the datasource input `DS_TEST-CLUSTER` resolves to a Prometheus datasource in the target Grafana instance.
- In Prometheus, verify every referenced metric family exists for a representative TiKV cluster and carries the expected labels.
- Exercise dashboard variables in Grafana: `k8s_cluster` should populate first, `tidb_cluster` should narrow by cluster, and `instance` should support the all/regex behavior used by panel queries.
- Open each row and confirm all 42 graph panels return data or intentional empty results on a known cluster.
- Spot-check histogram panels by verifying bucket, sum, and count series are present and that `histogram_quantile` output is finite.
- Test legacy alert import/evaluation for the ten embedded alert rules, especially `Critical error`, `Server report failures`, `Channel full`, `Approximate Region size`, and the thread CPU alerts.
- For migrations to newer Grafana versions, test conversion of legacy graph panels and panel alerts before relying on this file for production monitoring.
