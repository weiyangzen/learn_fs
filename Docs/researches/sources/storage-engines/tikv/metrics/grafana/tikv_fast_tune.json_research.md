# sources/storage-engines/tikv/metrics/grafana/tikv_fast_tune.json

## Purpose

`tikv_fast_tune.json` is a Grafana dashboard export named `Test-Cluster-TiKV-FastTune` with UID `TiKVFastTune`. It is a TiKV operational tuning and incident-triage dashboard focused on quickly identifying whether TiDB-visible write or read latency is caused by TiKV RPC imbalance, scheduler queues, raftstore/apply waiting, RocksDB write/read behavior, compaction backlog, PD scheduling activity, CPU jitter, or coprocessor pressure. The default time range is the last six hours, refreshes every five minutes, and uses browser timezone with Grafana dark styling.

The dashboard is organized as a sequence of row separators and graph panels. The first row, `Summary`, correlates write/read RPC rates and latency with write stalls, pending compaction bytes, PD scheduling, CPU, and other high-level causes. The `TiKV-Write affected TiDB-Write ?` row drills into write-path bottlenecks. The `TiKV-Read affected TiDB-Write ?` row covers read/coprocessor pressure that can interfere with write latency by consuming shared TiKV and RocksDB resources.

## Important APIs, Types, and Functions

This file has no executable functions, but it depends on Grafana's JSON dashboard schema and Prometheus query API:

- Dashboard schema fields include `__inputs`, `__requires`, `annotations`, `templating`, `panels`, `time`, `timepicker`, `refresh`, `uid`, and `version`.
- The datasource input is `DS_TEST-CLUSTER`, a Prometheus datasource reference substituted as `${DS_TEST-CLUSTER}` throughout templating and panel targets.
- The required Grafana components are Grafana `6.0.1`, Graph panel `5.0.0`, and Prometheus datasource `5.0.0`; the dashboard schema version is `18`.
- Template variables are hidden `k8s_cluster` and `tidb_cluster` selectors plus a visible multi-select `instance` selector. `instance` uses `includeAll` with `allValue: ".*"`, making it suitable for regex label filters.
- Panel targets use PromQL functions such as `rate`, `irate`, `delta`, `avg_over_time`, `sum`, `avg`, `max`, and `histogram_quantile` over one-minute windows.
- Graph panel behavior is mostly time-series driven, with legend formats such as `{{instance}}-write`, `write-rpc`, `duration-999%`, `pending-bytes-kv`, `rocksdb-cpu-{{instance}}`, and `{{type}}-max`.

The dashboard reads metrics from these major metric families: `tikv_grpc_msg_duration_seconds_*`, `tikv_engine_write_stall`, `tikv_engine_pending_compaction_bytes`, `pd_schedule_operators_count`, `pd_scheduler_store_status`, `tikv_worker_pending_task_total`, `node_cpu_seconds_total`, `tikv_futurepool_pending_task_total`, `tikv_raftstore_request_wait_time_duration_secs_bucket`, `tikv_raftstore_apply_wait_time_duration_secs_bucket`, `tikv_engine_write_micro_seconds`, `tikv_engine_flow_bytes`, `tikv_engine_compaction_flow_bytes`, `tikv_thread_cpu_seconds_total`, `tikv_engine_bytes_per_write`, `tikv_raftstore_store_perf_context_time_duration_secs_bucket`, `tikv_raftstore_apply_perf_context_time_duration_secs_bucket`, `tikv_engine_wal_file_sync_micro_seconds`, `tikv_coprocessor_request_*`, `tikv_coprocessor_scan_details`, `tikv_engine_get_micro_seconds`, `tikv_coprocessor_rocksdb_perf`, `tikv_engine_sst_read_micros`, `tikv_raftstore_proposal_total`, `tikv_engine_cache_efficiency`, `tikv_engine_locate`, `tikv_engine_seek_micro_seconds`, and `tikv_engine_get_served`.

## Control Flow

Grafana loads the dashboard, asks the configured Prometheus datasource to resolve template variables, then renders the graph panels using the selected label values. The variable flow is hierarchical: `k8s_cluster` is discovered from `tikv_engine_block_cache_size_bytes`, `tidb_cluster` is filtered by the selected Kubernetes cluster, and `instance` is filtered by both cluster labels through `tikv_engine_size_bytes`. Every panel query then injects these variables as `k8s_cluster="$k8s_cluster"`, `tidb_cluster="$tidb_cluster"`, and usually `instance=~"$instance"`.

At render time, the dashboard compares baseline traffic with suspected causes. Many panels include `write-rpc` as a reference series using `tikv_grpc_msg_duration_seconds_count` for `kv_prewrite`, `kv_commit`, and `kv_pessimistic_lock`. The summary row first checks imbalance and RPC latency across write, get/batch-get/scan, and coprocessor calls. It then checks write stalls, compaction pending bytes, PD scheduling operators, PD pending tasks, region balancing reasons, and CPU jitter. The write-impact row moves down the pipeline through scheduler future-pool queues, scheduler wait histograms, raftstore and apply wait histograms, RaftDB/KVDB write latency, compaction/frontend IO flows, RocksDB thread CPU, write batch sizes, mutex/write-thread wait, and RaftDB WAL sync latency. The read-impact row covers coprocessor QPS and handling latency, coprocessor wait queues, scan amplification, KVDB get/seek/SST/cache behavior, delete-skipped counts, and read-index/local-read fallback to raftstore.

The dashboard has 54 top-level panel entries, including three row separators and 51 graph panels, with 142 Prometheus target expressions. Rows are not collapsed, so all panels are visible in the exported layout.

## State and Persistence Behavior

The only persistent state in this source file is dashboard configuration. It does not store metric values, alerts, or user data. Grafana persists dashboard identity through `uid: "TiKVFastTune"`, `version: 7`, `iteration: 1606814402924`, and `editable: true`; `id` and `gnetId` are `null`, which makes the export portable across Grafana instances. Timepicker options and refresh intervals are embedded in the file, while actual time-series state remains in Prometheus.

Runtime state is provided by Grafana URL/template variable selections. The visible `instance` variable supports multi-select and all-instances regex selection; hidden `k8s_cluster` and `tidb_cluster` variables are still required for the datasource queries. Because all panels use short one-minute PromQL ranges, the dashboard emphasizes recent spikes and jitter rather than long-term smoothing.

## Dependencies and Integration Points

The dashboard integrates with a TiKV/TiDB deployment whose Prometheus labels include `k8s_cluster`, `tidb_cluster`, `instance`, and metric-specific labels such as `type`, `db`, `req`, `cf`, `name`, `store`, `event`, `mode`, and `metric`. It also integrates with PD metrics for scheduling-operator and store-capacity context, and node exporter CPU metrics through `node_cpu_seconds_total`.

Operationally, this dashboard is a companion to TiDB/TiKV incident response. It assumes Prometheus scrapes TiKV, PD, and node metrics with consistent cluster labels. It also assumes TiKV exposes legacy metric names used by the dashboard, including RocksDB-engine percentile gauge families such as `tikv_engine_write_micro_seconds`, `tikv_engine_seek_micro_seconds`, and `tikv_engine_sst_read_micros`.

## Risks and Edge Cases

- Metric-name drift is the primary maintenance risk. If TiKV renames or removes legacy metric families, panels silently show no data.
- Some query filters are hard-coded to specific operation labels, for example write RPCs as `kv_prewrite|kv_commit|kv_pessimistic_lock` and read RPCs as `kv_get|kv_scan|kv_batch_get|kv_batch_get_command|coprocessor`. New RPC names will be absent until the regexes are updated.
- Many queries aggregate across instances with `sum` or `avg`, which is useful for cluster-level diagnosis but can hide one bad instance unless paired with the per-instance panels.
- Histogram quantiles are computed after summing buckets. This is appropriate for aggregate latency, but it differs from taking per-instance quantiles and can obscure skew.
- Several panels correlate write RPCs with non-write causes; correlation is visual rather than causal. Operators still need to confirm causality with logs, deployment events, and workload changes.
- Panel titles contain question marks and one note that scheduler wait duration is incorrectly included. Those labels are useful for triage but should not be treated as formal alert definitions.
- Short one-minute `rate` windows make the dashboard sensitive to scrape gaps and low-volume workloads.

## Test Signals

Validation should start with JSON parsing and Grafana import. A useful static check is `jq` parsing plus a traversal that counts panels and target expressions, verifies every PromQL target has a datasource, and confirms the three template variables resolve against Prometheus. Runtime validation should open the dashboard against a representative TiKV cluster and verify that high-level Summary panels, write-path panels, and read/coprocessor panels all return data.

Prometheus query checks should cover representative expressions for RPC histograms, RocksDB gauges, future-pool queues, raftstore/apply wait buckets, PD schedule operator counts, node CPU, and coprocessor metrics. For regression testing, compare panel counts, target counts, UID, required datasource input, and variable names after any dashboard edit.
