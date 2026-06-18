# Research: sources/storage-engines/tikv/metrics/grafana/tikv_details.json

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008906`: lines 1-8022, `Docs/researches/chunks/subset-b-008906_research.md`
- `subset-b-008907`: lines 8023-15657, `Docs/researches/chunks/subset-b-008907_research.md`
- `subset-b-008908`: lines 15658-22524, `Docs/researches/chunks/subset-b-008908_research.md`
- `subset-b-008909`: lines 22525-30293, `Docs/researches/chunks/subset-b-008909_research.md`
- `subset-b-008910`: lines 30294-37416, `Docs/researches/chunks/subset-b-008910_research.md`
- `subset-b-008911`: lines 37417-45105, `Docs/researches/chunks/subset-b-008911_research.md`
- `subset-b-008912`: lines 45106-52917, `Docs/researches/chunks/subset-b-008912_research.md`
- `subset-b-008913`: lines 52918-60535, `Docs/researches/chunks/subset-b-008913_research.md`
- `subset-b-008914`: lines 60536-68613, `Docs/researches/chunks/subset-b-008914_research.md`
- `subset-b-008915`: lines 68614-76906, `Docs/researches/chunks/subset-b-008915_research.md`
- `subset-b-008916`: lines 76907-85424, `Docs/researches/chunks/subset-b-008916_research.md`
- `subset-b-008917`: lines 85425-86952, `Docs/researches/chunks/subset-b-008917_research.md`

## Chunk Research

### subset-b-008906: lines 1-8022

# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 1-8022

## Scope

This chunk covers the opening 8,022 lines of the TiKV detailed Grafana dashboard JSON. It starts with dashboard-level metadata and the Prometheus datasource input `DS_TEST-CLUSTER`, then defines the `Duration`, `Cluster`, `Errors`, and `Server` row panels through the beginning of the final `gRPC resource group QPS` panel. The slice ends mid-object at the `xaxis.name` field for that panel, so the full JSON document continues in later chunks.

The content is declarative dashboard configuration rather than executable TiKV code. Its effective behavior is the set of Grafana panels, legends, axes, thresholds, and Prometheus expressions used to observe TiKV write/read latency, cluster resources, error signals, storage/raft internals, scheduler/thread-pool behavior, RocksDB perf counters, and gRPC server traffic.

## Purpose

- Provide the first major monitoring surface for TiKV details in Grafana, backed by a Prometheus datasource selected through `${DS_TEST-CLUSTER}`.
- Organize TiKV health into collapsed Grafana rows: `Duration`, `Cluster`, `Errors`, and `Server`.
- Expose latency distributions with `histogram_quantile()` over Prometheus histogram buckets and expose average values with `rate(_sum) / rate(_count)`.
- Track per-instance capacity, CPU, memory, disk utilization, RocksDB flow, QPS, error rates, leader/region counts, and uptime.
- Surface failure and saturation conditions such as critical errors, scheduler busy, channel full, coprocessor full, write stall, raftstore process busy, report-failure messages, leader missing, damaged RocksDB files, and raft append rejects.
- Break down server-side request paths by gRPC type, priority, source, resource group, batch sizes, batch wait latency, and raft message batch size.

## Important Dashboard Objects And Queries

- Dashboard metadata declares one Prometheus input named `DS_TEST-CLUSTER` and uses old-style Grafana graph panels with `renderer: "flot"`, `type: "graph"`, `type: "row"`, `gridPos`, `legend`, `tooltip`, `xaxis`, and `yaxes` fields.
- The `Duration` row contains:
  - `Write Pipeline Duration`, a stacked bar graph with quantiles for `tikv_raftstore_append_log_duration_seconds_bucket`, `tikv_raftstore_request_wait_time_duration_secs_bucket`, `tikv_raftstore_apply_wait_time_duration_secs_bucket`, `tikv_raftstore_commit_log_duration_seconds_bucket`, and `tikv_raftstore_apply_log_duration_seconds_bucket`.
  - `Cop Read Duration`, a stacked bar graph with `tikv_storage_engine_async_request_duration_seconds_bucket{type="snapshot"}`, `tikv_coprocessor_request_wait_seconds_bucket{type="all"}`, and `tikv_coprocessor_request_handle_seconds_bucket`.
- The `Cluster` row includes store capacity panels from `tikv_store_size_bytes{type="used|available|capacity"}`, CPU from `process_cpu_seconds_total` with hidden `tikv_server_cpu_cores_quota`, memory from `process_resident_memory_bytes` with hidden `tikv_server_memory_quota_bytes`, disk utilization from `node_disk_io_time_seconds_total`, MBps from `tikv_engine_flow_bytes` and `tikv_in_memory_engine_flow`, QPS from `tikv_grpc_msg_duration_seconds_count`, error rate from `tikv_grpc_msg_fail_total`, missing PD heartbeat detection via `tikv_pd_heartbeat_message_total{type="noop"} < 1`, critical errors from `tikv_critical_error_total`, leader/region counts from `tikv_raftstore_region_count`, and uptime from `time() - process_start_time_seconds`.
- The `Errors` row begins with `Critical error`, which adds a Grafana threshold at values greater than zero, then aggregates operational failure signals in `Server is busy`: `tikv_scheduler_too_busy_total`, `tikv_channel_full_total`, `tikv_coprocessor_request_error{type="full"}`, `tikv_engine_write_stall{type="write_stall_percentile99",db=~"$db"}`, `tikv_raftstore_store_write_msg_block_wait_duration_seconds_count`, and `tikv_raftstore_process_busy`.
- Additional `Errors` panels include server report failures through `tikv_server_report_failure_msg_total`, RocksDB/engine size via `tikv_engine_size_bytes`, channel full by type, active written leaders and write distributions from `tikv_region_written_keys_*` and `tikv_region_written_bytes_*`, approximate region size from `tikv_raftstore_region_size_*`, clear-overlap-region duration from `tikv_raftstore_clear_overlap_region_duration_seconds_*`, apply key/value size buckets, hibernated peer state, raftstore memory trace through `tikv_server_mem_trace_sum{name=~"raftstore-.*"}` plus `raft_engine_memory_usage`, raft entry cache evictions through `tikv_raft_entries_evict_bytes`, address-resolution latency through `tikv_server_address_resolve_duration_secs_bucket`, and raft append rejects through `tikv_server_raft_append_rejects`.
- The `Server` row starts at the end of the chunk and covers gRPC/server panels:
  - `gRPC message count`, `gRPC message failed`, quantile `gRPC message duration$optional_quantile`, and `Average gRPC message duration` using `tikv_grpc_msg_duration_seconds_*` and `tikv_grpc_msg_fail_total`, with variants grouped by `type`, `priority`, and `$additional_groupby`.
  - `gRPC batch commands wait duration` from `tikv_grpc_batch_commands_wait_duration_seconds_bucket`.
  - `gRPC batch size` from request/response batch histograms and averages: `tikv_server_grpc_req_batch_size_*`, `tikv_server_grpc_resp_batch_size_*`, and `tikv_server_request_batch_size_*`.
  - `raft message batch size` from `tikv_server_raft_message_batch_size_*`.
  - `gRPC request sources QPS` and `gRPC request sources duration` from `tikv_grpc_request_source_counter_vec` and `tikv_grpc_request_source_duration_vec`.
  - `gRPC resource group QPS` from `tikv_grpc_resource_group_total`; this panel continues past line 8022.

## Control Flow And Data Flow

Grafana loads the dashboard JSON, resolves the `DS_TEST-CLUSTER` input to a Prometheus datasource, and renders each collapsed row when expanded. Each graph panel executes its `targets` against Prometheus using dashboard variables such as `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$db`, `$optional_quantile`, `$additional_groupby`, and Grafana's `$__rate_interval`.

Most panels follow one of four PromQL patterns. Counter and histogram streams use `rate(metric[$__rate_interval])` for per-second behavior. Histogram quantiles wrap `histogram_quantile(q, sum(rate(bucket[$__rate_interval])) by (le, ...))`. Average latencies or sizes divide `sum(rate(metric_sum))` by `sum(rate(metric_count))`. Gauges and current state use direct `sum(metric) by (...)`, `avg(metric) by (...)`, or expressions such as `time() - process_start_time_seconds`.

The row layout is declarative. Parent row panels have `collapsed: true`, `type: "row"`, and nested `panels`. Child panels carry the actual Prometheus targets and presentation settings. Legends commonly sort by max or current value, hide empty and zero series, and render on the right as a table.

## State And Persistence Behavior

This chunk has no runtime state inside TiKV and does not persist user data. It is persisted as repository configuration for Grafana. At deployment/import time it becomes Grafana dashboard state: panel IDs, row collapse state, grid positions, datasource binding, PromQL expressions, units, thresholds, hidden targets, and legend rules.

The dashboard reads TiKV, process, node, and raft-engine metrics from Prometheus. It does not write to TiKV, Prometheus, or Grafana datasources during normal viewing. Its persistence impact is indirect: changing a query, label selector, unit, or threshold changes what operators see and can therefore affect alert triage, capacity decisions, and incident diagnosis.

## Dependencies And Integration Points

- Grafana dashboard import/runtime must support this JSON schema and legacy graph panel options such as `aliasColors`, `bars`, `lines`, `renderer: "flot"`, `seriesOverrides`, `thresholds`, `tooltip`, `xaxis`, and `yaxes`.
- Prometheus is the only datasource declared in this slice. Every target uses `${DS_TEST-CLUSTER}`.
- Query selectors depend on TiDB Operator or deployment labels `k8s_cluster`, `tidb_cluster`, and `instance`. Some panels also depend on `job=~".*tikv"`, `db=~"$db"`, `type`, `priority`, `source`, `name`, `req`, `store_id`, `state`, and `$additional_groupby`.
- TiKV metric integration spans raftstore, storage engine, coprocessor, scheduler, server, gRPC, YATP thread pool, RocksDB perf, memory trace, and in-memory engine metrics.
- Non-TiKV metric integration includes `process_cpu_seconds_total`, `process_resident_memory_bytes`, `process_start_time_seconds`, `node_disk_io_time_seconds_total`, and `raft_engine_memory_usage`.
- Panel units integrate with Grafana formatting: seconds (`s`), bytes (`bytes`), operations (`ops`), percent unit (`percentunit`), and untyped counts (`none`/`short`).

## Risks And Edge Cases

- The assigned chunk ends inside a panel object, so validating only lines 1-8022 as standalone JSON will fail. Validation must use the full `tikv_details.json` or merge all chunks first.
- Several expressions include `$additional_groupby` directly inside `by (...)`. If that variable expands to an empty or malformed value, PromQL can become invalid or produce unexpected grouping.
- Hidden quota series for CPU and memory are present but hidden. Operators may miss quota context unless they intentionally enable those series or a later dashboard version surfaces them.
- `IO utilization` groups by `instance` but its legend includes `{{device}}`; without grouping by `device`, the legend can show an empty or misleading device label.
- Error panels often use `null as zero` and `hideZero`. That keeps dashboards quiet, but it can hide missing series, scrape gaps, or label mismatches unless Prometheus/Grafana missing-data behavior is tested separately.
- Critical-error thresholding is present on the `Critical error` panel, but most other error/saturation panels are visual only in this chunk. Operational alerting must exist elsewhere if non-zero values should page.
- Histogram quantiles depend on correct `_bucket` series and complete `le` labels. Dropped buckets, aggregation across incompatible label sets, or low traffic can make quantiles noisy.
- Average expressions divide `_sum` rates by `_count` rates without explicit zero guards. For sparse traffic windows, panels can show `NaN`, `Inf`, or disappear depending on Prometheus/Grafana behavior.
- Regex filters such as `job=~".*tikv"` and `db=~"$db"` can over-match if label conventions drift.
- The chunk mixes TiKV metrics with process/node metrics; dashboard correctness depends on consistent relabeling so `instance` refers to comparable entities across all jobs.
- Metric renames or label changes in TiKV, raft-engine, or deployment exporters will silently break panels until dashboard tests or visual review catch missing series.

## Test Signals

- Parse the full `tikv_details.json` with a JSON parser and Grafana dashboard linter after all chunks are reconciled; do not parse this chunk alone as JSON.
- Run PromQL syntax checks for every `expr` in this chunk with representative variable expansions for `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$db`, `$optional_quantile`, `$additional_groupby`, and `$__rate_interval`.
- In a TiKV test cluster, verify that each panel returns at least one series when the relevant workload runs: writes for write-pipeline panels, coprocessor reads for read panels, raft traffic for raft panels, and gRPC traffic for server panels.
- Check histogram panels with both high and low traffic to confirm quantiles and average divisions render acceptably when `_count` rates are zero or sparse.
- Verify label grouping and legends, especially `IO utilization`, gRPC priority/type groupings, resource group names, request sources, raftstore memory names, and report-failure `store_id`.
- Confirm the `Critical error` threshold renders when `tikv_critical_error_total` is non-zero and that zero/missing series behavior is understood for panels using `hideZero` and `null as zero`.
- Compare all metric names in this slice against TiKV's exported metrics after a version upgrade, with special attention to older names ending in `_duration_secs_bucket`, vector-style names such as `tikv_grpc_request_source_counter_vec`, and raft-engine memory metrics.
- Import the dashboard into a supported Grafana version and expand the `Duration`, `Cluster`, `Errors`, and `Server` rows to verify panel layout, units, hidden series, and row collapse behavior.

### subset-b-008907: lines 8023-15657

# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 8023-15657

## Scope

This chunk covers a middle segment of the TiKV details Grafana dashboard JSON. It starts at the tail of the preceding `gRPC` row, then defines the collapsed `Storage`, `Local Reader`, `Thread CPU`, and `IO Breakdown` rows. The range ends inside panel `113` in the following `Raft Waterfall` row's first latency panels, so the last panel is visible enough to identify its purpose and queries but continues past the chunk boundary.

The content is dashboard configuration rather than executable code. Its "APIs" are Grafana panel schemas, Prometheus datasource targets, dashboard template variables, and PromQL expressions tied to TiKV metric names.

## Purpose

The chunk builds operational observability for TiKV storage-path latency, local read routing, thread-level CPU attribution, disk IO throughput, IO rate limiting, and early raft waterfall latency. It lets operators answer questions such as:

- how many storage commands TiKV is receiving by `type`;
- whether async engine requests are failing;
- how write, snapshot, local-read snapshot, read-index propose, and read-index confirm latency distributions behave;
- whether full compaction is consuming or pausing storage work;
- whether local reads are accepted, rejected, stale, or follower reads;
- which TiKV thread pools are consuming CPU;
- whether read/write IO volume or rate limiter wait time is high;
- where raft request latency is accumulating between async write, store, apply, propose wait, and batch wait phases.

## Important Dashboard Objects

- Row `61`, title `Storage`, collapsed with 17 child panels. It groups storage command rates, async request errors, heatmaps and percentile graphs for async request durations, process CPU, full compaction timings, and concurrency manager timestamps.
- Row `79`, title `Local Reader`, collapsed with 2 child panels. It tracks local read rejection reasons and received/executed local read request rates.
- Row `82`, title `Thread CPU`, collapsed with 20 child panels. It groups `tikv_thread_cpu_seconds_total` by regex-matched TiKV thread names and exposes busy non-RocksDB threads over 80 percent CPU.
- Row `103`, title `IO Breakdown`, collapsed with 4 child panels. It tracks write/read IO bytes, IO rate limiter thresholds, and rate limiter request wait duration.
- Row `108`, title `Raft Waterfall`, is visible from the full JSON structure and begins in this chunk with panels `109` through `113`. This chunk includes async write, store, apply, store propose wait, and store batch wait latency panels; panel `113` continues past line 15657.

All panels use the Prometheus datasource template `${DS_TEST-CLUSTER}` except row containers, which have null datasources. Most queries are filtered by dashboard variables `k8s_cluster="$k8s_cluster"`, `tidb_cluster="$tidb_cluster"`, `instance=~"$instance"`, and many aggregate by `$additional_groupby`. Latency and rate panels use Grafana's `$__rate_interval`; the IO rate limiter quantile panel uses `$optional_quantile`.

## Metrics And Query Patterns

The `Storage` row uses these main metrics:

- `tikv_storage_command_total`: command receive rate, grouped by `type` and `$additional_groupby`.
- `tikv_storage_engine_async_request_total`: async engine request error rate, filtering `status!~"all|success"`.
- `tikv_storage_engine_async_request_duration_seconds_bucket/_sum/_count`: async request histograms for `type="write"`, `type="snapshot"`, `type="snapshot_local_read"`, `type="snapshot_read_index_propose_wait"`, and `type="snapshot_read_index_confirm"`.
- `tikv_storage_process_stat_cpu_usage`: storage process CPU usage over the panel-described 30 second window.
- `tikv_storage_full_compact_duration_seconds_*`, `tikv_storage_full_compact_pause_duration_seconds_*`, and `tikv_storage_full_compact_increment_duration_seconds_*`: full compaction latency, pause latency, and per-increment latency.
- `tikv_concurrency_manager_max_ts_limit` and `tikv_concurrency_manager_max_ts`: concurrency manager timestamp progress and limit.

The latency graph pattern is repeated throughout this chunk: each graph overlays 99.99th percentile, 99th percentile, average, and count series. Percentiles are computed with `histogram_quantile(...)` over `sum(rate(<metric>_bucket[$__rate_interval])) by (le, $additional_groupby)`. Averages divide the rate of `_sum` by the rate of `_count`, and counts use the rate of `_count`. Heatmap companions use `sum(increase(<metric>_bucket[$__rate_interval])) by (le)`.

The `Local Reader` row uses:

- `tikv_raftstore_local_read_reject_total`, grouped by `instance` and `reason`;
- `tikv_raftstore_local_read_executed_requests`, `_executed_stale_read_requests`, `_executed_follower_read_requests`, `_received_requests`, `_received_stale_read_requests`, and `_received_follower_read_requests`, each rendered as rates grouped by `$additional_groupby`.

The `Thread CPU` row uses `tikv_thread_cpu_seconds_total` and regex filters on `name`:

- raftstore: `(raftstore|rs)_.*`;
- async apply: `apply_[0-9]+`;
- store writer: `store_write.*`;
- gRPC: `grpc.*`;
- scheduler: `sched_.*`;
- unified read pool: `unified_read_po.*`;
- RocksDB: `rocksdb.*`;
- GC, region, snapshot, background, raftlog fetch, import, backup, CDC, TSO, storage read pool, coprocessor read pool, and IME each have dedicated regexes.

The busy-thread panel uses `topk(20, sum(rate(tikv_thread_cpu_seconds_total{name!~"rocksdb.*"}[$__rate_interval])) by (instance, name) > 0.8)`, so it is an exception panel that surfaces only non-RocksDB threads above the 80 percent threshold.

The `IO Breakdown` row uses:

- `tikv_io_bytes{op="write"}` and `tikv_io_bytes{op="read"}` for per-type and total throughput;
- `tikv_rate_limiter_max_bytes_per_sec` for IO threshold by priority/type;
- `tikv_rate_limiter_request_wait_duration_seconds_*` for configurable quantile and average wait duration.

The visible part of `Raft Waterfall` uses:

- `tikv_storage_engine_async_request_duration_seconds_*{type="write"}`;
- `tikv_raftstore_store_duration_secs_*`;
- `tikv_raftstore_apply_duration_secs_*`;
- `tikv_raftstore_request_wait_time_duration_secs_*`;
- `tikv_raftstore_store_wf_batch_wait_duration_seconds_*`.

## Control Flow

Runtime flow is declarative and driven by Grafana:

1. Grafana loads the dashboard JSON and renders row panels.
2. Dashboard variables supply datasource, cluster, instance, grouping, rate interval, and optional quantile values.
3. Each panel sends its `targets[].expr` PromQL query to the selected Prometheus-compatible datasource.
4. Prometheus evaluates rate, increase, sum, avg, histogram, and top-k expressions against TiKV's exported metric series.
5. Grafana renders graph or heatmap panels, applies legend formatting, axis units, null handling, and series overrides.

There are no local functions, classes, or imperative branches in this JSON. The main control-flow-like behavior is the repeated composition of histogram bucket, sum/count, and count queries into a single graph panel and the use of collapsed rows to defer visual expansion in Grafana.

## State And Persistence Behavior

The chunk contributes persistent dashboard configuration. It does not mutate TiKV state, Prometheus state, or Grafana runtime state directly. Its persistence effects are through stored dashboard JSON: panel IDs, titles, grid positions, query text, legend formats, axis formats, and row membership remain stable until edited or regenerated.

Important persistent identifiers in this chunk include panel IDs `61` through `113`. These IDs are used by Grafana for panel references, links, snapshots, and dashboard diffs. Most panels set `nullPointMode` to `null as zero`, hide empty/zero legend series, and sort legends by maximum descending; this affects incident interpretation because missing series may be visually suppressed or flattened to zero.

## Dependencies And Integration Points

- Grafana dashboard schema: row, graph, heatmap, `gridPos`, `fieldConfig`, `legend`, `tooltip`, `xaxis`, `yaxes`, and series override fields.
- Prometheus query language: `rate`, `increase`, `sum`, `avg`, `histogram_quantile`, `topk`, regex label filters, and grouping clauses.
- TiKV metric exporters: all metric names in this chunk must remain emitted with expected labels such as `k8s_cluster`, `tidb_cluster`, `instance`, `type`, `status`, `reason`, `name`, `op`, and histogram `le`.
- Dashboard templating: `${DS_TEST-CLUSTER}`, `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$additional_groupby`, `$__rate_interval`, and `$optional_quantile`.
- Operational runbooks and alerts may depend on panel titles and metric semantics even if no alert rules are embedded in this chunk.

## Risks

- Query drift risk: if TiKV renames metrics or thread names, panels silently go empty. This is especially likely for regex-based thread panels such as `unified_read_po.*`, `(backup-worker|bkwkr|backup_endpoint).*`, and CDC/TSO naming variants.
- Label-cardinality risk: `$additional_groupby` can expand every latency and IO panel by arbitrary grouping labels. High-cardinality groupings can make Grafana slow and Prometheus queries expensive.
- Histogram correctness risk: `histogram_quantile` requires preserving `le` in the aggregation. This chunk does so, but any future edit that removes `le` would make percentiles invalid.
- Average correctness risk: averages divide `_sum` rate by `_count` rate. If count is zero or missing for a grouping, Prometheus can produce empty or invalid-looking series.
- Visual interpretation risk: `null as zero`, hidden empty/zero legends, and negative-Y transforms for count series can make absence of data look like zero work or hide instrumentation failures.
- Boundary risk: the chunk ends in panel `113`; later chunks must reconcile the rest of `Store batch wait duration` and any subsequent `Raft Waterfall` panels before producing the final per-file research.
- Duplicate semantics risk: `Storage async write duration` appears both in the `Storage` row and in the beginning of `Raft Waterfall`. This is likely intentional for different diagnostic contexts, but dashboard maintenance must keep the duplicated queries consistent.

## Test Signals

Useful validation signals include:

- Parse the file with `jq` to confirm valid JSON and stable panel nesting for rows `61`, `79`, `82`, `103`, and `108`.
- Use a Grafana dashboard linter or provisioning dry-run to ensure graph and heatmap panel fields are accepted by the target Grafana version.
- Run Prometheus API query checks for representative expressions from each row against a TiKV test cluster: `tikv_storage_command_total`, `tikv_storage_engine_async_request_duration_seconds_bucket`, `tikv_raftstore_local_read_reject_total`, `tikv_thread_cpu_seconds_total`, `tikv_io_bytes`, and `tikv_rate_limiter_request_wait_duration_seconds_bucket`.
- Verify every histogram quantile query groups by `le` plus any intended label dimensions.
- Verify dashboard variables expand safely when `$additional_groupby` is empty or contains one or more labels.
- Compare rendered panels before and after any dashboard edit with a cluster that has storage traffic, local reads, raftstore activity, compaction, and IO rate limiter activity.

### subset-b-008908: lines 15658-22524

# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 15658-22524

## Scope

This chunk covers a middle slice of the TiKV details Grafana dashboard JSON. The range begins inside the final target of the `Store batch wait duration` graph and ends inside the first target of `99% Apply log duration per server`, so both boundary panels are partial in this chunk. The complete material visible here includes:

- The tail of the collapsed `Raft Waterfall` row: store writer waterfall latency panels from `Store batch wait duration` through `Store commit and persist duration`.
- The complete collapsed `Raftstore IO` row: paired heatmap and percentile graph panels for raftstore IO reasons such as peer destroy, peer creation, stale merge checks, snapshot reads, v2 learner compatibility, raft term lookup, and raft log fetch.
- The beginning of the collapsed `Raft IO` row: process-ready, store-write-loop, append-log, commit-log, and apply-log latency panels.

The file is dashboard configuration, not executable code. Its effective APIs are Grafana panel schemas, Prometheus expressions, dashboard variables, metric names, labels, and row/panel layout contracts.

## Purpose

This section defines operational visibility for Raftstore write-path and IO latency in TiKV. It turns TiKV Prometheus histogram metrics into Grafana rows that let an operator diagnose where raft work is waiting: request batching, proposal send, store writer queueing, KV DB state writes, Raft Engine writes, leader persistence, commit/persist timing, peer creation/destruction IO, raft log reads, raft append/commit/apply phases, and store write-loop behavior.

The chunk uses two visual idioms repeatedly:

- Heatmap panels show bucket distribution over time with `sum(increase(<histogram>_bucket[$__rate_interval])) by (le)`.
- Graph panels show high percentiles, mean latency, and event rate with `histogram_quantile(0.9999, ...)`, `histogram_quantile(0.99, ...)`, `<sum>/<count>`, and `sum(rate(<count>[$__rate_interval]))`.

Most graph panels set the latency y-axis to seconds and put count series on the second y-axis with a negative transform through the `alias` `/^count/` override. This lets latency and throughput be inspected together without the count line hiding the latency curves.

## Important Dashboard Objects

### Raft Waterfall Tail

The chunk starts in panel `113`, `Store batch wait duration`, with only its final count query and panel footer visible. It then contains complete graph panels `114` through `121`:

- `Store send to write queue duration` uses `tikv_raftstore_store_wf_send_to_queue_duration_seconds`.
- `Store send proposal duration` uses `tikv_raftstore_store_wf_send_proposal_duration_seconds`.
- `Store write kv db end duration` uses `tikv_raftstore_store_wf_write_kvdb_end_duration_seconds`.
- `Store before write duration` uses `tikv_raftstore_store_wf_before_write_duration_seconds`.
- `Store write end duration` uses `tikv_raftstore_store_wf_write_end_duration_seconds`.
- `Store persist duration` uses `tikv_raftstore_store_wf_persist_duration_seconds`.
- `Store commit but not persist duration` uses `tikv_raftstore_store_wf_commit_not_persist_log_duration_seconds`.
- `Store commit and persist duration` uses `tikv_raftstore_store_wf_commit_log_duration_seconds`.

These panels all follow the same four-target pattern: 99.99th percentile, 99th percentile, average from histogram sum/count, and count rate. They group by `$additional_groupby`; unlike the later per-server panels, these waterfall graphs do not add `instance` to the aggregation key in this chunk.

The collapsed row object is titled `Raft Waterfall` and contains the panels as nested `panels` entries. The row itself has no query targets.

### Raftstore IO Row

Collapsed row `122`, `Raftstore IO`, is complete in this chunk. It contains twelve IO reason pairs. Each reason has a heatmap panel using `tikv_raftstore_io_duration_seconds_bucket` and a graph panel using the corresponding bucket/sum/count series filtered by the same `reason` label:

- `peer_destroy_kv_write`: RocksDB write when destroying a peer.
- `peer_destroy_raft_write`: RaftEngine write when destroying a peer.
- `init_raft_state`: raft-state initialization when creating a peer.
- `init_apply_state`: apply-state initialization when creating a peer.
- `entry_storage_create`: RaftEngine read operation when creating a peer.
- `store_check_msg`: checking region state for a message to a non-existent region.
- `peer_check_merge_target_stale`: checking stale merged regions.
- `peer_maybe_create`: RocksDB and RaftEngine reads while creating a peer.
- `peer_snapshot_read`: read requests for peer snapshot work.
- `v2_compatible_learner`: raftstore v2 compatibility checking.
- `raft_term`: reading terms of raft logs from RaftEngine.
- `raft_fetch_log`: fetching raft logs from RaftEngine.

The heatmap side of each pair has one target, `format: "heatmap"`, `legendFormat: "{{le}}"`, `maxDataPoints: 512`, `dataFormat: "tsbuckets"`, hidden zero buckets, and a seconds y-axis. The graph side has four targets: 99.99%, 99%, average, and count. These graph targets group by `instance`, `le` where needed, and `$additional_groupby`, so they preserve per-TiKV-server latency differences.

### Raft IO Row Beginning

Collapsed row `147`, `Raft IO`, begins at line 21053 and is partially included. Complete pairs visible in this chunk are:

- `Process ready duration` and `99% Process ready duration per server`, using `tikv_raftstore_raft_process_duration_secs` filtered by `type="ready"`.
- `Store write loop duration` and `99% Store write loop duration per server`, using `tikv_raftstore_store_write_loop_duration_seconds`.
- `Append log duration` and `99% Append log duration per server`, using `tikv_raftstore_append_log_duration_seconds`.
- `Commit log duration` and `99% Commit log duration per server`, using `tikv_raftstore_commit_log_duration_seconds`.
- `Apply log duration`, a complete heatmap using `tikv_raftstore_apply_log_duration_seconds_bucket`.

Panel `157`, `99% Apply log duration per server`, starts in this chunk but is not complete here. The visible target is the 99.99th percentile query over `tikv_raftstore_apply_log_duration_seconds_bucket` grouped by `instance`, `le`, and `$additional_groupby`; the remaining targets continue after the chunk boundary.

## Query and Control Flow

There is no application control flow, but there is a consistent dashboard data flow:

1. Grafana variables such as `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$additional_groupby`, and `$__rate_interval` are substituted into PromQL.
2. Prometheus filters TiKV series by Kubernetes cluster, TiDB cluster, and instance regex.
3. Histogram bucket panels either aggregate bucket increases by `le` for heatmaps or aggregate bucket rates by `le` plus grouping labels for `histogram_quantile`.
4. Average lines divide rate of `_sum` by rate of `_count`.
5. Count lines use rate of `_count`, grouped consistently with the panel.
6. Grafana renders nested row panels as collapsed sections, preserving the row-local `gridPos` layout.

The panel order expresses troubleshooting flow more than execution flow. The waterfall panels follow raftstore write progress from scheduling through queueing, proposal, local write, persistence, and commit. The IO row then breaks down specific peer and raftstore maintenance IO reasons. The Raft IO row begins lower-level raft processing timings for ready processing, write-loop work, log append, log commit, and log apply.

## State and Persistence Behavior

The JSON persists dashboard state: panel IDs, row collapse state, layout, legends, query strings, y-axis units, color/heatmap settings, data source references, and target visibility. It does not persist TiKV runtime state.

Runtime state is external:

- TiKV exposes histogram metrics through Prometheus scrape endpoints.
- Prometheus stores bucket, sum, and count time series for the configured retention period.
- Grafana computes rates, increases, quantiles, averages, and visual transformations at query/render time.

Because row objects are `collapsed: true`, their nested panels are persisted inside the row's `panels` array. Tools that flatten or migrate Grafana JSON must preserve nested row panels or the dashboard will lose these views.

## Dependencies and Integration Points

The chunk depends on:

- Grafana's legacy graph and heatmap panel schemas (`type: "graph"` and `type: "heatmap"`), including flot rendering options, row nesting, series overrides, and axis configuration.
- The dashboard data source variable `${DS_TEST-CLUSTER}`.
- Prometheus-compatible PromQL functions: `rate`, `increase`, `sum by`, and `histogram_quantile`.
- TiKV metric names emitted by raftstore instrumentation, including `tikv_raftstore_store_wf_*`, `tikv_raftstore_io_duration_seconds`, `tikv_raftstore_raft_process_duration_secs`, `tikv_raftstore_store_write_loop_duration_seconds`, `tikv_raftstore_append_log_duration_seconds`, `tikv_raftstore_commit_log_duration_seconds`, and `tikv_raftstore_apply_log_duration_seconds`.
- Label contracts for `k8s_cluster`, `tidb_cluster`, `instance`, `reason`, `type`, `le`, and whatever labels are supplied through `$additional_groupby`.

Operationally, this section integrates TiKV raftstore metrics with cluster dashboards used for diagnosing raft latency, peer lifecycle IO, Raft Engine read/write cost, and store-io-pool behavior.

## Risks

- The chunk has partial panels at both boundaries. `Store batch wait duration` and `99% Apply log duration per server` must be reconciled with adjacent chunks before producing the final per-file research document.
- The dashboard uses legacy Grafana panel types and nested collapsed rows. Grafana migrations can change field names or handling of row-contained panels.
- `histogram_quantile` requires preserving `le` in the aggregation key. Dropping `le` would make percentile panels invalid; adding or removing `instance` changes whether a graph is cluster-wide or per-server.
- The average expression divides rate of `_sum` by rate of `_count`; panels do not guard against zero count denominators beyond hiding empty or zero legend values.
- `$additional_groupby` is interpolated directly into `by (...)` clauses. If it is empty or malformed for the deployed Grafana/Prometheus version, queries can fail or group differently than expected.
- Heatmaps aggregate only by `le`, while corresponding graph panels often group by `instance` and `$additional_groupby`. This is intentional for distribution overview versus server-specific percentile detail, but it can surprise operators comparing the two views.
- Metric name or label drift in TiKV instrumentation will silently break affected panels unless dashboard validation or runtime query checks catch it.
- Count series are transformed to negative values on a second y-axis; consumers reading screenshots must understand that downward count curves do not mean negative events.

## Test and Validation Signals

Useful validation for this chunk is dashboard and metric oriented:

- Run JSON validation with `jq` over `tikv_details.json` to confirm the file remains syntactically valid after edits.
- Import the dashboard into a Grafana version supported by the project and verify that collapsed rows `Raft Waterfall`, `Raftstore IO`, and `Raft IO` render nested panels.
- Query a TiKV Prometheus target for each metric family named in this chunk and confirm bucket, sum, and count series exist with the expected labels.
- Validate representative PromQL expressions for each pattern: a waterfall graph, a raftstore IO heatmap, a raftstore IO per-server graph, a raft-process `type="ready"` graph, and an apply-log graph.
- Check that percentile graph legends show 99.99%, 99%, avg, and count series and that count series are assigned to the secondary y-axis.
- Exercise Grafana variables `$k8s_cluster`, `$tidb_cluster`, `$instance`, and `$additional_groupby` with both broad and narrow selections to catch empty result sets and invalid grouping expansions.

### subset-b-008909: lines 22525-30293

# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 22525-30293

## Scope and Purpose

This chunk is a contiguous slice of the TiKV Details Grafana dashboard JSON. It contains the tail of a Raft IO/apply-log panel, then complete collapsed rows for Raft IO, Raft Propose, Raft Process, Raft Message, and most of Raft Admin before ending inside the first Raft log GC panel. The file is declarative dashboard configuration rather than executable code, so the important "APIs" are Grafana panel fields, Prometheus query expressions, dashboard variables, and the TiKV metric names those expressions depend on.

The slice focuses on diagnosing TiKV Raftstore behavior: Raft client wait-ready latency, store write blocking, proposal rates and wait times, apply/store FSM scheduling and polling, unpersisted-apply state, Raft message throughput/drop/latency, admin command activity, split/load-base-split behavior, flashback-state peers, and the start of raft-log-GC write latency.

## Dashboard Structure and Panels

- The chunk starts mid-panel with `99% Apply log duration per server`, using `tikv_raftstore_apply_log_duration_seconds_*` to show p99, hidden average, and hidden count by `instance` plus `$additional_groupby`.
- `Raft IO` row includes `Raft Client Wait Connection Ready Duration`, `99% Raft Client Wait Connection Ready Duration`, `Store io task reschedule`, and `Write task block duration per server $optional_quantile`.
- `Raft Propose` row includes proposal count and latency panels: `Raft proposals per ready`, `Raft read/write proposals`, read/write proposals per server, propose wait heatmap and p99/p99.99 graph, store write wait heatmap and percentile graph, apply wait heatmap and percentile graph, store-write handle duration, write trigger size, propose-log throughput, and perf-context duration.
- `Raft Process` row includes ready handling, max raftstore event duration, replica-read lock-check duration, FSM reschedules, store/apply FSM schedule wait, store/apply FSM poll duration, store/apply FSM poll rounds, store/apply FSM count per poll, peer/apply message length distributions, unpersisted-apply region count, and apply-ahead-of-persistence log count.
- `Raft Message` row includes sent, flushed, received, accepted-by-type, vote, and dropped-message panels, plus send-wait and receive-delay heatmaps and p99/p99.99 graphs.
- `Raft Admin` row includes admin proposals, admin apply, split-check count and duration, load-base split event/duration, observed CPU/QPS/read bytes for load-base split decisions, peer flashback-state count, and begins `Raft log GC write duration`.

Panel layout is Grafana's legacy graph/heatmap schema. Repeated fields include `gridPos`, `id`, `legend`, `seriesOverrides`, `tooltip`, `xaxis`/`yaxes` or heatmap `xAxis`/`yAxis`, `nullPointMode: "null as zero"`, and `${DS_TEST-CLUSTER}` datasource binding. Most graph legends are configured as right-side tables sorted by `max` descending with empty and zero series hidden.

## Important Query Patterns

- Histogram heatmaps use `sum(increase(<metric>_bucket{...}[$__rate_interval])) by (le)` and set `format: "heatmap"` with `dataFormat: "tsbuckets"` in heatmap panels.
- Percentile graphs use `histogram_quantile(...)` over `sum(rate(<metric>_bucket{...}[$__rate_interval])) by (..., le, $additional_groupby)`. Fixed quantiles include `0.99`, `0.9999`, `0.999999`, `1`, and `0.8`; several panels use `$optional_quantile`.
- Average overlays divide rate of `_sum` by rate of `_count`, usually hidden or styled with a filled line. Count overlays use `_count` and are frequently hidden or transformed to negative Y on the second axis.
- Counter/rate panels use `sum(rate(...[$__rate_interval])) by (...)`. Gauge-like panels use direct `sum((metric{...})) by (...)`, and load-base split events use `sum(delta(tikv_load_base_split_event[1m]))`.
- Every query filters by `k8s_cluster="$k8s_cluster"`, `tidb_cluster="$tidb_cluster"`, and usually `instance=~"$instance"`. Several panels add label filters such as `type="ready"`, `type="send_wait"`, `type="receive_delay"`, `type=~"local_read|normal|read_index"`, `type!=="compact"` is not used; the actual PromQL filter is `type!="compact"`.
- `$additional_groupby` is injected into many `by (...)` clauses and legend templates. This is the main integration knob for drilling into extra labels, but it must expand to a syntactically valid group-by list for every affected PromQL expression.

## Metrics Covered

The chunk references these TiKV metrics:

- Raft IO and apply/write path: `tikv_raftstore_apply_log_duration_seconds_*`, `tikv_server_raft_client_wait_ready_duration_*`, `tikv_raftstore_io_reschedule_region_total`, `tikv_raftstore_io_reschedule_pending_tasks_total`, `tikv_raftstore_store_write_msg_block_wait_duration_seconds_bucket`.
- Proposal path: `tikv_raftstore_apply_proposal_bucket`, `tikv_raftstore_proposal_total`, `tikv_raftstore_request_wait_time_duration_secs_*`, `tikv_raftstore_store_write_task_wait_duration_secs_*`, `tikv_raftstore_apply_wait_time_duration_secs_*`, `tikv_raftstore_store_write_handle_msg_duration_secs_bucket`, `tikv_raftstore_store_write_trigger_wb_bytes_bucket`, `tikv_raftstore_propose_log_size_sum`, `tikv_raftstore_apply_perf_context_time_duration_secs_bucket`, `tikv_raftstore_store_perf_context_time_duration_secs_bucket`.
- Raft process/FSM path: `tikv_raftstore_raft_ready_handled_total`, `tikv_raftstore_raft_process_duration_secs_count`, `tikv_raftstore_event_duration_bucket`, `tikv_broadcast_normal_duration_seconds_bucket`, `tikv_replica_read_lock_check_duration_seconds_bucket`, `tikv_batch_system_fsm_reschedule_total`, `tikv_batch_system_fsm_schedule_wait_seconds_bucket`, `tikv_batch_system_fsm_poll_seconds_bucket`, `tikv_batch_system_fsm_poll_rounds_bucket`, `tikv_batch_system_fsm_count_per_poll_bucket`, `tikv_raftstore_peer_msg_len_bucket`, `tikv_raftstore_apply_msg_len_bucket`, `tikv_raft_enable_unpersisted_apply_regions`, `tikv_raft_apply_ahead_of_persist_bucket`.
- Raft messaging: `tikv_raftstore_raft_sent_message_total`, `tikv_server_raft_message_flush_total`, `tikv_server_raft_message_recv_total`, `tikv_raftstore_raft_dropped_message_total`, `tikv_server_raft_message_duration_seconds_*`.
- Admin/split/flashback/log-GC path: `tikv_raftstore_admin_cmd_total`, `tikv_raftstore_check_split_total`, `tikv_raftstore_check_split_duration_seconds_bucket`, `tikv_load_base_split_event`, `tikv_load_base_split_duration_seconds_*`, `tikv_load_base_split_region_load_*`, `tikv_raftstore_peer_in_flashback_state`, and `tikv_raftstore_raft_log_gc_write_duration_secs_*`.

## Control Flow and Observability Model

Grafana evaluates this JSON by row and panel. Collapsed row panels are stored inside the row object's `panels` array; when a row is expanded in Grafana, each child panel runs its PromQL targets against the selected Prometheus datasource and dashboard variables. There is no application control flow in the JSON itself, but there is an implicit diagnostic flow:

1. Raft IO panels surface whether raft log application, raft-client connection readiness, IO rescheduling, or store-write blocking are introducing latency.
2. Raft Propose panels break client-facing Raft work into proposal volume, read/write mix, request wait time, store write wait, apply wait, write message handling, write batch trigger size, proposed log throughput, and RocksDB perf-context latency.
3. Raft Process panels distinguish ready processing, batch-system scheduling, poll duration, poll rounds, message batch sizes, and unpersisted-apply lag. These panels help identify scheduler saturation versus Raftstore execution cost.
4. Raft Message panels isolate network/transport behavior: send/flush/receive rate, message type mix, vote churn, explicit dropped messages, local send wait, and receiver-reported receive delay.
5. Raft Admin panels track control-plane actions that can explain workload shifts: conf-change/transfer-leader proposals, admin apply commands, split checks, load-base split events and decision inputs, flashback-state peers, and raft-log-GC write latency.

The panels intentionally combine heatmaps for distribution shape with percentile/average/count graphs for per-instance attribution. This makes the dashboard useful for first seeing a cluster-wide tail and then drilling down to the responsible TiKV instance or label group.

## State and Persistence Behavior

The JSON persists dashboard state only: panel IDs, grid placement, row collapse state, legend preferences, axis units, datasource references, query strings, and variable placeholders. It does not persist TiKV runtime state. The observed state is pulled from Prometheus time series produced by TiKV and selected through dashboard variables.

Several panels encode persistence-related semantics indirectly:

- `tikv_raft_enable_unpersisted_apply_regions` reports regions applying unpersisted raft logs.
- `tikv_raft_apply_ahead_of_persist_bucket` reports the raft-log gap between applied and persisted indexes.
- `tikv_raftstore_raft_log_gc_write_duration_secs_*`, visible at the end of the chunk, monitors write latency for raft log GC state changes.
- Proposal, store-write, apply-wait, and raft-ready panels together expose where durable Raft progress is delayed.

Because Prometheus queries use `rate`, `increase`, and `delta`, the dashboard depends on scrape continuity and monotonically increasing counter semantics. Counter resets, missing scrapes, or label cardinality changes will directly affect panel continuity.

## Dependencies and Integration Points

- Grafana legacy panel model: `graph`, `heatmap`, collapsed `row`, `seriesOverrides`, `legend`, and axis/tooltip fields.
- Prometheus datasource `${DS_TEST-CLUSTER}` and Grafana interval variable `$__rate_interval`.
- Dashboard variables: `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$additional_groupby`, and `$optional_quantile`.
- TiKV metric exporters for raftstore, server raft messaging, batch system, replica read, broadcast, and load-base split metrics.
- TiKV operational workflows: Raft proposal/read-index debugging, apply/write path latency analysis, batch system/FSM scheduling, raft transport diagnosis, admin/split diagnosis, flashback monitoring, and raft log GC diagnosis.

## Risks and Edge Cases

- Query syntax is sensitive to `$additional_groupby`. If it expands to an empty value or includes a leading/trailing comma in the wrong context, PromQL `by (...)` clauses can fail or produce unexpected grouping.
- High-cardinality groupings on `instance`, `to`, `type`, `reason`, and `$additional_groupby` can make histogram quantiles expensive, especially p99.99/p99.9999-style panels over bucket metrics.
- Some panel descriptions are inaccurate or typo-prone. `Store io task reschedule` says "throughput of disk write per IO type" but queries reschedule counters; `Apply fsm schedule wait duration` has a trailing `e`; `Perf Context duration` repeats a proposal-rate description; and `Store io task reschedule` legend uses `rechedule`.
- Several graphs set `nullPointMode` to `null as zero`. Missing series can look like true zeros, which is useful for quiet panels but risky during scrape gaps.
- `histogram_quantile(1, ...)` for apply-ahead-of-persistence approximates the top bucket boundary, not an exact maximum. Operators should not treat it as a precise per-region max.
- `sum(delta(tikv_load_base_split_event[1m]))` can show negative or confusing values around counter resets if the metric behaves like a counter rather than an event gauge.
- Unit handling is mixed: CPU millicores are divided by `1000`, read bytes are described as KiB, proposal speed uses bytes/sec, and many count overlays are hidden or on a secondary axis. Incorrect axis units can lead to false comparisons between panels.
- The file chunk ends inside the `Raft log GC write duration` panel, so any following targets or panels must be reconciled from the next chunk before producing the final per-file report.

## Test Signals

Since this is dashboard JSON, useful validation is configuration and query validation rather than unit testing:

- Parse the full `tikv_details.json` as JSON and ensure this chunk remains structurally nested under the intended row/panel objects after edits.
- Use Grafana dashboard import or provisioning validation to catch invalid legacy panel fields, duplicate panel IDs, bad row nesting, and datasource variable issues.
- Run Prometheus `api/v1/query` or `promtool`-style checks against representative expressions after variable substitution, especially expressions containing `$additional_groupby` and `$optional_quantile`.
- Verify all referenced metric names still exist in TiKV's metrics registry/exported `/metrics` output; missing `_bucket`, `_sum`, or `_count` siblings will break percentile or average panels.
- Exercise dashboard variable combinations: no extra group-by, grouping by `instance`, grouping by message/admin `type`, and a filtered `$instance` regex.
- Visually smoke-test the heatmaps and graph legends in Grafana with a live cluster to ensure bucket formats, axis units, hidden average/count overlays, and negative-Y count transforms render as intended.

## Cross-Chunk Notes

This work item starts in the middle of the preceding Raft IO/apply-log panel and ends in the middle of the Raft Admin `Raft log GC write duration` panel. The final merged per-file research should combine this analysis with adjacent chunks to recover the complete row context, preceding panel IDs, the remainder of the log-GC panel, later Raft Admin panels, dashboard templating definitions, and top-level dashboard metadata.

### subset-b-008910: lines 30294-37416

# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 30294-37416

## Scope and Purpose

This chunk is a mid-dashboard section of the TiKV Grafana details dashboard. It closes the collapsed `Raft Log` row, defines the full collapsed `Raft Engine` row, and begins the collapsed `RocksDB - $db` row. The file is declarative Grafana JSON, so its operational surface is the panel schema plus the embedded PromQL query contracts against TiKV, raft-engine, Prometheus, and Grafana dashboard variables.

The chunk gives operators drill-down visibility into three storage paths:

- Raft log GC and asynchronous raft log fetching, including GC write/seek rates, skipped/failed GC, raft log lag, fetch counts, and fetch worker queue depth.
- Raft Engine write/read/rewrite/WAL behavior, including operation rates, high-percentile write duration, write-size distribution, WAL sub-phase latency, log file and entry counts, and compression ratio.
- RocksDB engine behavior for the selected `$db`, including get/seek/write/WAL/compaction/cache/key/read/write panels through `Bytes / Read` at panel id 262.

## Dashboard Structure

The chunk contains these row/panel groups:

- `Raft Log` row ending at panel id 225. Visible panels in this chunk are ids 218-225.
- `Raft Engine` collapsed row id 226. Nested panels are ids 227-236.
- `RocksDB - $db` collapsed row id 237. Nested panels in this chunk are ids 238-262; the row continues after the chunk.

All panels use the old Grafana graph panel shape: `"type": "graph"`, `renderer: "flot"`, `xaxis.mode: "time"`, `targets` arrays containing Prometheus `expr`/`query`, and `legend` tables configured with current/max values, max sorting, and hidden empty/zero series. Most panels use `${DS_TEST-CLUSTER}` as the datasource and cluster selectors `{k8s_cluster="$k8s_cluster", tidb_cluster="$tidb_cluster", instance=~"$instance"}`. RocksDB panels also add `db="$db"` and often group by `$additional_groupby`.

## Important APIs, Types, and Query Contracts

There are no code-defined functions or classes in this JSON. The important "APIs" are the Grafana dashboard schema fields, the PromQL functions, and the metric names this dashboard assumes are exported.

Grafana-facing contracts:

- Row panels use `collapsed: true` and hold their child graphs in a `panels` array. This keeps the detailed storage sections folded until an operator expands them.
- Graph panels rely on `gridPos` to lay out mostly 12-wide, 7-high paired panels, with some 24-wide panels such as `Raft log async fetch task duration`.
- `targets[].expr` and `targets[].query` duplicate the same PromQL, a compatibility pattern for older Grafana/Prometheus datasource JSON.
- `legendFormat` depends on labels such as `instance`, `type`, `reason`, `cf`, and the template-expanded `$additional_groupby`.
- Units are set through `yaxes[].format`: `s`, `ops`, `binBps`, `bytes`, `percentunit`, `µs`, `short`, or `none`. Several latency panels use logarithmic axes.

PromQL contracts:

- Counter-like metrics are converted with `sum(rate(metric{...}[$__rate_interval])) by (...)`.
- Histogram metrics use `histogram_quantile(...)` over `sum(rate(..._bucket[$__rate_interval])) by (le, ...)`, with average lines computed as `sum(rate(..._sum)) / sum(rate(..._count))`.
- Gauge-like metrics use `avg((metric{...}))`, `sum((metric{...}))`, `max((metric{...}))`, or `topk(20, avg(...))` without `rate`.
- Dashboard variables used directly in PromQL include `$__rate_interval`, `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$additional_groupby`, `$optional_quantile`, and `$db`.

Key metric families in this chunk:

- Raft log GC/fetch: `tikv_raftstore_raft_log_kv_sync_duration_secs_*`, `tikv_raftstore_raft_log_gc_write_duration_secs_count`, `tikv_raftstore_raft_log_gc_seek_operations_count`, `tikv_raftstore_log_lag_sum`, `tikv_raftstore_raft_log_gc_skipped`, `tikv_raftstore_raft_log_gc_failed`, `tikv_raftstore_entry_fetches`, `tikv_raftstore_entry_fetches_task_duration_seconds_*`, and `tikv_worker_pending_task_total{name=~"raftlog-fetch-worker"}`.
- Raft Engine: `raft_engine_write_apply_duration_seconds_*`, `raft_engine_read_entry_duration_seconds_*`, `raft_engine_read_message_duration_seconds_*`, `raft_engine_write_duration_seconds_*`, `raft_engine_write_size_*`, `raft_engine_background_rewrite_bytes_sum`, `raft_engine_write_preprocess_duration_seconds_bucket`, `raft_engine_write_leader_duration_seconds_bucket`, `raft_engine_sync_log_duration_seconds_bucket`, `raft_engine_allocate_log_duration_seconds_bucket`, `raft_engine_rotate_log_duration_seconds_bucket`, `raft_engine_log_file_count`, `raft_engine_swap_file_count`, `raft_engine_recycled_file_count`, `raft_engine_purge_duration_seconds_bucket`, `raft_engine_log_entry_count`, and `raft_engine_write_compression_ratio_*`.
- RocksDB engine: `tikv_engine_memtable_efficiency`, `tikv_engine_cache_efficiency`, `tikv_engine_get_served`, `tikv_engine_get_micro_seconds`, `tikv_engine_locate`, `tikv_engine_seek_micro_seconds`, `tikv_engine_write_served`, `tikv_engine_write_micro_seconds`, `tikv_engine_wal_file_synced`, `tikv_engine_write_wal_time_micro_seconds`, `tikv_engine_event_total`, `tikv_engine_num_running_compactions`, `tikv_engine_num_running_flushes`, `tikv_raftstore_compaction_guard_action_total`, `tikv_engine_compaction_time`, `tikv_engine_num_files_in_single_compaction`, `tikv_engine_sst_read_micros`, `tikv_engine_compaction_reason`, `tikv_engine_block_cache_size_bytes`, `tikv_engine_bloom_efficiency`, `tikv_engine_flow_bytes`, `tikv_engine_compaction_num_corrupt_keys`, `tikv_engine_estimate_num_keys`, and `tikv_engine_bytes_per_read`.

## Panel-Level Behavior

Raft log panels:

- `Raft log GC kv sync duration` id 218 plots 99.99th percentile and average KV sync latency by instance.
- `Raft log GC write operations` id 219 and `Raft log GC seek operations` id 220 show per-instance GC write and seek operation rates.
- `Raft log lag` id 221 charts raft log lag by instance from `tikv_raftstore_log_lag_sum`.
- `Raft log gc skipped` id 222 groups skipped GC by `instance, reason`; `Raft log GC failed` id 223 tracks failure rate.
- `Raft log fetch` id 224 groups fetch rates by `type` and `$additional_groupby`.
- `Raft log async fetch task duration` id 225 combines a 99.99th percentile fetch-task histogram, an average fetch-task latency line, and a pending-task gauge for `raftlog-fetch-worker`. The pending-task series is overridden onto the right axis and transformed as negative Y, which makes queue buildup visually distinct from duration.

Raft Engine panels:

- `Operation` id 227 compares write-apply, read-entry, and read-message operation rates.
- `Write Duration` id 228 overlays 99.99th percentile, 99th percentile, average, and hidden count for `raft_engine_write_duration_seconds`. Count is configured as a dashed negative right-axis series; average stays on the left axis.
- `Flow` id 229 shows raft-engine write bytes plus background rewrite bytes by rewrite `type`.
- `Write Duration Breakdown $optional_quantile` id 230 splits write latency into preprocess/wait, leader/WAL, and apply stages at the selected quantile.
- `Bytes / Written` id 231 mirrors the write-duration pattern for write size histograms, with percentile, average, and count series.
- `WAL Duration Breakdown (999%)` id 232 breaks WAL write latency into total, sync, allocate, and rotate at 0.999 quantile.
- `File Count` id 233 and `Entry Count` id 235 monitor log/swap/recycled files and log entries.
- `Other Durations $optional_quantile` id 234 covers read-entry, read-message, and purge histogram latencies.
- `Write Compression Ratio` id 236 shows high-percentile, average, and count series from raft-engine compression-ratio histograms.

RocksDB panels in this chunk:

- `Get operations` id 238 compares memtable hits, block cache hits, and L0/L1/L2-and-up get serving rates.
- `Get duration` id 239 and `Seek duration` id 241 use already-exported max/percentile/average gauge series in microseconds rather than deriving quantiles from buckets.
- `Seek operations` id 240 tracks seek/next/prev and found variants through `tikv_engine_locate`.
- `Write operations` id 242 distinguishes successful writes, timeouts, and WAL writes.
- `Write duration` id 243, `Write WAL duration` id 245, `WAL sync duration` id 247, `Compaction duration` id 249, `Compaction Job Size(files)` id 250, `SST read duration` id 251, and `Bytes / Read` id 262 all follow the same max/99/95/avg gauge-series pattern.
- `WAL sync operations` id 244 tracks sync rate.
- `Compaction operations` id 246 combines completed compaction/flush event rates on the left axis with running compaction/flush gauges on the right axis.
- `Compaction guard actions` id 248 groups raftstore compaction guard action rates by `cf`, `type`, and `$additional_groupby`, limited to `default|write` column families.
- `Compaction reason` id 252 groups compaction rates by `cf` and `reason`.
- `Block cache size` id 253 uses `topk(20, avg(tikv_engine_block_cache_size_bytes) by (cf, instance))`, so it intentionally caps displayed cache-size series.
- `Memtable hit` id 254, `Block cache hit` id 256, and bloom-prefix efficiency use ratio expressions of hit-like counters over hit-plus-miss or filtered-plus-match counters.
- `Block cache flow` id 255 covers read/write byte flow and data/filter/index insert/evict byte rates.
- `Keys flow` id 257 adds read/written key rates and corrupt-key compaction rate.
- `Block cache operations` id 258 counts cache add/add-failure operations by cache component.
- `Read flow` id 259, `Total keys` id 260, and `Write flow` id 261 show bytes read, estimated keys, WAL bytes, and write bytes.

## Control Flow and Data Flow

Grafana evaluates this chunk from dashboard variables to PromQL queries to panel rendering:

1. The user selects datasource, cluster, instance regex, `$additional_groupby`, optional quantile, and RocksDB `$db`.
2. Expanding a collapsed row materializes its nested graph panels.
3. For each visible panel, Grafana sends each target expression to the Prometheus datasource over the dashboard time range.
4. Prometheus filters TiKV/raft-engine metrics by the dashboard labels, applies `rate`, `sum`, `avg`, `max`, `topk`, or `histogram_quantile`, and groups by the requested labels.
5. Grafana renders each returned series using the panel title, legend format, unit, axis, and optional series override.

There is no local mutation or branching logic in the JSON. The effective behavior is controlled by metric availability, template variable expansion, Prometheus aggregation semantics, and Grafana rendering options.

## State and Persistence Behavior

This chunk persists dashboard state only as JSON configuration:

- Panel identity and layout are stored in stable numeric `id` and `gridPos` fields.
- Query state is embedded in each target's `expr`/`query`; no runtime query results are persisted in the repository.
- Collapsed rows persist their child panels under `panels`, so the dashboard starts compact while retaining detailed storage diagnostics.
- Visibility/interpretation state is encoded through `hide`, `seriesOverrides`, axis units, log bases, `nullPointMode: "null as zero"`, and legend sorting.

Runtime metric state lives outside this file in Prometheus. The dashboard assumes TiKV and raft-engine exporters provide compatible metric names and labels.

## Dependencies and Integration Points

Primary dependencies:

- Grafana graph panel JSON compatible with legacy/flot graph panels.
- Grafana Prometheus datasource `${DS_TEST-CLUSTER}`.
- Prometheus with TiKV and raft-engine metrics scraped under labels `k8s_cluster`, `tidb_cluster`, `instance`, and for RocksDB panels `db`.
- Dashboard templating variables `$instance`, `$additional_groupby`, `$optional_quantile`, `$db`, `$k8s_cluster`, `$tidb_cluster`, and `$__rate_interval`.

Integration points:

- Operators use these panels to correlate raftstore log GC/fetch symptoms with raft-engine WAL/write behavior and RocksDB compaction/cache behavior.
- Raft Engine panels depend on the raft-engine metric prefix rather than the older RocksDB/TiKV `tikv_engine_*` prefix.
- RocksDB panels integrate column-family labels (`cf`) and reason/type labels, making them sensitive to label cardinality and exporter naming.
- The `Compaction guard actions` panel bridges raftstore metrics into the RocksDB row, showing that storage layout and raftstore region compaction guard behavior are intentionally observed together.

## Risks and Edge Cases

- `$additional_groupby` is interpolated inside `by (...)` clauses. If it expands to an empty or malformed label list, PromQL can become invalid or produce unexpected grouping.
- Several average expressions divide rate sums by count rates. When counts are zero, Prometheus can return `NaN`/`Inf`; Grafana's `null as zero` may mask missing traffic as zero.
- `nullPointMode: "null as zero"` can make scrape gaps or missing metric series look like real zero values.
- High-cardinality grouping by `instance`, `cf`, `reason`, `type`, and arbitrary `$additional_groupby` values can create heavy Prometheus queries, especially histogram quantiles across bucket series.
- The dashboard mixes histogram-derived quantiles for raft-engine with exporter-provided percentile gauges for RocksDB. The two forms have different statistical meaning and aggregation behavior.
- Panel id 253 uses `topk(20)`, intentionally hiding all but the largest 20 block-cache size series.
- Some panel titles and labels contain cosmetic inconsistencies, such as trailing spaces, `999%` wording for 0.999 quantile, and `{{ type}}` with an extra space in the legend template. These do not necessarily break Grafana but can reduce polish or make legend matching brittle.
- Series overrides that transform count/pending-task series to negative Y are visually useful but can be misread as negative metric values if operators do not know the convention.
- The chunk assumes metric families such as `raft_engine_*` and `tikv_engine_*` retain exact names and label values. Exporter renames, TiKV version drift, or raft-engine feature-gating would silently empty panels.

## Test and Validation Signals

Useful validation checks for this chunk:

- Parse the dashboard with `jq` to ensure JSON syntax remains valid and panel ids 218-262 are present with expected titles.
- Load the dashboard in Grafana and expand `Raft Log`, `Raft Engine`, and `RocksDB - $db` rows to confirm nested panels render and do not show datasource/query syntax errors.
- Run representative PromQL queries from each family in Prometheus: one histogram quantile, one average `_sum/_count` expression, one `$optional_quantile` query, one RocksDB percentile gauge, one ratio expression, and one `topk` expression.
- Test dashboard variables with normal and edge selections: all instances, a single instance, each `$db` value, and each `$additional_groupby` option.
- Verify metric availability for the expected exporters by checking that panels for raft log GC, raft-engine write/WAL, RocksDB compaction, and block cache all return non-empty series on an active TiKV cluster.
- Inspect rendered units and axes: seconds for histogram latencies, microseconds for RocksDB gauge latencies, bytes/binBps for flow/size panels, percentunit for hit ratios, and right-axis overrides for pending/running/count series.

### subset-b-008911: lines 37417-45105

# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 37417-45105

## Chunk Scope

This chunk covers the TiKV details Grafana dashboard from the tail of the RocksDB row through the full Titan row and the beginning of the In Memory Engine row. It is dashboard configuration rather than executable application code, but it defines an operational API between TiKV Prometheus metrics and Grafana panels. The chunk uses the dashboard-level Prometheus datasource `${DS_TEST-CLUSTER}` and the templated labels `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$db`, `$titan_db`, `$additional_groupby`, and Grafana's `$__rate_interval`.

The visible panels are:

- RocksDB `$db` metrics: compaction flow, bytes per write, read amplification, pending compaction bytes, snapshots, compression ratio, SST file levels, oldest snapshot duration, external SST ingestion, RocksDB block-read counters, write stall signals, stall-condition changes, and memtable size.
- Titan `$titan_db` metrics: blob file count and size, blob cache size and hit ratio, blob key/value size distributions, blob get and iterator operations, blob read/write/sync/GC durations, blob flow rates, discardable ratio distribution, and GC input/output/file counters.
- In Memory Engine start: KV operations, read throughput comparison with RocksDB, coprocessor handle duration, region cache hit and hit-rate, region cache miss reasons, and memory usage. The next panel starts at the end of the chunk but is incomplete here.

## Purpose

The chunk's purpose is to expose low-level TiKV storage engine health in one dashboard area. Operators can use these panels to correlate:

- RocksDB write amplification, compaction pressure, memtable growth, stalled writes, snapshot retention, and ingestion behavior.
- Titan blob-file lifecycle, cache effectiveness, blob I/O latency, iterator behavior, discardable data accumulation, and GC throughput.
- In-memory engine usage, hit rate, request latency, and read throughput contribution relative to RocksDB.

This dashboard is a read-only observability artifact. It does not persist TiKV state, mutate cluster configuration, or run application control flow. Its behavioral contract is the set of PromQL expressions, units, labels, legend templates, row layout, and Grafana panel options encoded in JSON.

## Important Dashboard Objects and APIs

The primary "types" in this chunk are Grafana dashboard schema objects:

- `row` panels: `RocksDB - $db`, `Titan - $titan_db`, and `In Memory Engine` organize nested panels and are collapsed by default in surrounding dashboard style.
- `graph` panels: most panels use the legacy `flot` graph renderer, line rendering, table legends, `hideEmpty: true`, `hideZero: true`, `sort: "max"`, and `nullPointMode: "null as zero"`.
- `heatmap` panel: `Ingestion picked level` uses bucketed `tikv_engine_ingestion_picked_level_bucket` data with `sum(increase(...[$__rate_interval])) by (le)`.
- Prometheus query APIs: `rate`, `increase`, `sum`, `avg`, `max`, `topk`, and `histogram_quantile`.
- Prometheus histogram convention: duration panels use `_bucket`, `_sum`, and `_count` series for percentile, average, and request-rate views.

Important metrics referenced by family:

- RocksDB engine flow and state: `tikv_engine_compaction_flow_bytes`, `tikv_engine_flow_bytes`, `tikv_engine_bytes_per_write`, `tikv_engine_read_amp_flow_bytes`, `tikv_engine_pending_compaction_bytes`, `tikv_engine_num_snapshots`, `tikv_engine_compression_ratio`, `tikv_engine_num_files_at_level`, `tikv_engine_oldest_snapshot_duration`, `tikv_engine_memory_bytes`.
- Ingestion and RocksDB perf: `tikv_engine_ingestion_picked_level_bucket`, `tikv_storage_ingest_external_file_duration_secs_bucket`, `_sum`, `_count`, `tikv_storage_ingest_external_file_allow_write_counter`, `tikv_storage_rocksdb_perf`, `tikv_coprocessor_rocksdb_perf`.
- Write stall: `tikv_engine_write_stall_reason`, `tikv_engine_write_stall`, `tikv_engine_stall_conditions_changed`.
- Titan file and cache state: `tikv_engine_titandb_num_live_blob_file`, `tikv_engine_titandb_num_obsolete_blob_file`, `tikv_engine_titandb_live_blob_file_size`, `tikv_engine_titandb_obsolete_blob_file_size`, `tikv_engine_blob_cache_size_bytes`, `tikv_engine_blob_cache_efficiency`.
- Titan operation and latency families: `tikv_engine_blob_iter_touch_blob_file_count`, `tikv_engine_blob_key_size`, `tikv_engine_blob_value_size`, `tikv_engine_blob_locate`, `tikv_engine_blob_get_micros_seconds`, `tikv_engine_blob_seek_micros_seconds`, `tikv_engine_blob_next_micros_seconds`, `tikv_engine_blob_prev_micros_seconds`, `tikv_engine_blob_file_read_micros_seconds`, `tikv_engine_blob_file_write_micros_seconds`, `tikv_engine_blob_file_sync_micros_seconds`, `tikv_engine_blob_gc_micros_seconds`.
- Titan flow and GC: `tikv_engine_blob_flow_bytes`, `tikv_engine_titandb_blob_file_discardable_ratio`, `tikv_engine_blob_file_synced`, `tikv_engine_blob_gc_action_count`, `tikv_engine_blob_gc_flow_bytes`, `tikv_engine_blob_gc_input_file`, `tikv_engine_blob_gc_output_file`, `tikv_engine_blob_gc_file_count`.
- In-memory engine: `tikv_in_memory_engine_kv_operations`, `tikv_in_memory_engine_flow`, `tikv_in_memory_engine_memory_usage_bytes`, `tikv_snapshot_type_count`, `tikv_in_memory_engine_snapshot_acquire_failed_reason_count`, `tikv_coprocessor_request_handle_seconds_bucket`, `_sum`, `_count`.

## Query and Control Flow

Grafana drives control flow by evaluating each panel target over the selected time range and template variable values:

1. The dashboard variables resolve cluster and instance filters from Prometheus labels. In this chunk, all query targets filter by `k8s_cluster="$k8s_cluster"` and `tidb_cluster="$tidb_cluster"`, most filter by `instance=~"$instance"`, and storage-engine panels further filter by either `db="$db"` or `db="$titan_db"`.
2. Rate panels compute per-second changes over `$__rate_interval` using `rate(counter[$__rate_interval])` and then aggregate with `sum ... by (...)`.
3. Gauge-style panels read the current series and aggregate with `avg`, `max`, or `sum`.
4. Histogram panels calculate high-percentile latency with `histogram_quantile` over `sum(rate(bucket[$__rate_interval])) by (le, ...)`, and average latency with `sum(rate(_sum)) / sum(rate(_count))`.
5. Legends derive series identity from labels such as `instance`, `cf`, `level`, `type`, `req`, `ratio`, and `$additional_groupby`.

RocksDB flow:

- `Compaction flow` compares compaction bytes read, compaction bytes written, and flush-write bytes. It is the first correlation point for compaction I/O pressure.
- `Bytes / Write` reads precomputed summary-like series split by type labels `bytes_per_write_max`, `bytes_per_write_percentile99`, `bytes_per_write_percentile95`, and `bytes_per_write_average`.
- `Read amplification` divides total read bytes by estimated useful bytes per instance.
- Compaction backlog, snapshot counts/duration, compression ratio, SST file count, ingestion level, and ingest duration then provide cause signals for stalls and space amplification.
- `Write Stall Reason`, `Write stall duration`, and `Stall conditions changed of each CF` expose RocksDB throttle state and frequency.
- `Memtable size` tracks `type="mem-tables-all"` memory by column family.

Titan flow:

- File count and size panels compare live versus obsolete blob files.
- Cache panels show top 20 blob cache sizes by instance/CF and compute hit ratio as hit / (hit + miss).
- Size-distribution panels expose average, p95, p99, and max key/value/blob-iterator touch counts from `type` labels.
- Operation panels use `tikv_engine_blob_locate` counters for get, seek, prev, and next operations.
- Latency panels use pre-aggregated type labels ending in `_average`, `_percentile95`, `_percentile99`, and `_max`, grouped by either `$additional_groupby` or `type, $additional_groupby`.
- Flow panels split key and byte flows with `type=~"keys.*"` and `type=~"bytes.*"`.
- GC panels expose action counts, GC duration, input/output file sizes, key/byte flows, and file count rates.

In-memory engine flow:

- `OPS` sums `tikv_in_memory_engine_kv_operations` by `instance`, `type`, and `$additional_groupby`.
- `Read MBps` compares RocksDB `tikv_engine_flow_bytes` against `tikv_in_memory_engine_flow` for read and iterator read byte types.
- `Coprocessor Handle duration` shows 99.99%, 99%, average, and count for `tikv_coprocessor_request_handle_seconds` by request type.
- `Region Cache Hit` and `Region Cache Hit Rate` derive in-memory snapshot usage from `tikv_snapshot_type_count`.
- `Region Cache Miss Reason` breaks snapshot acquisition failures down by `type`.
- `Memory Usage` averages `tikv_in_memory_engine_memory_usage_bytes` by instance.

## State and Persistence Behavior

The chunk does not define durable application state. Persistence-related behavior is indirect:

- RocksDB panels reflect persisted LSM state: SST levels, compaction debt, snapshots, memtables, write stalls, and ingestion.
- Titan panels reflect persisted blob-file state: live/obsolete blob files, discardable ratios, blob GC input/output, and sync/write/read latencies.
- In-memory engine panels reflect volatile cache state and memory usage, with hit-rate calculations derived from snapshot acquisition counters.

Grafana state consists of dashboard JSON fields: panel `id`, `gridPos`, row nesting, datasource references, target expressions, legend display options, axis units, and rendering settings. This state is versionable configuration in the repository, not runtime state in TiKV.

## Dependencies and Integration Points

Runtime dependencies:

- Prometheus datasource `${DS_TEST-CLUSTER}`.
- TiKV metric exporters exposing the named `tikv_*` series and expected labels.
- Grafana support for legacy `graph`/`heatmap` panel JSON, `flot` rendering, table legends, and template variables.
- Dashboard-level variables from the full file, especially `k8s_cluster`, `tidb_cluster`, `db`, `instance`, `titan_db`, `additional_groupby`, and Grafana's `$__rate_interval`.

Integration points:

- The `$db` variable is sourced from RocksDB block-cache metrics and is reused across RocksDB panels.
- The `$titan_db` variable is sourced from Titan blob-file metrics and gates all Titan panels.
- `$additional_groupby` is injected directly into `by (...)` clauses, so it controls whether panels aggregate at cluster, instance, store, or other label dimensions.
- In-memory engine panels integrate with coprocessor request metrics and RocksDB read-flow metrics to compare cache behavior against regular engine reads.
- The row/panel IDs in this chunk (`263` through `314`) are part of the larger `tikv_details.json` dashboard and must stay unique within the full dashboard.

## Risks and Edge Cases

- Several panels use `nullPointMode: "null as zero"`. Missing series can appear as zero, which is convenient for sparse metrics but can hide exporter regressions or metric name drift.
- Ratio panels do not guard against zero denominators. `Read amplification`, `Blob cache hit`, and `Region Cache Hit Rate` may produce `NaN`, `Inf`, or missing series when useful bytes, hit+miss totals, or snapshot counts are zero.
- `$additional_groupby` appears inside `by (...)` clauses. If the variable is empty or malformed, PromQL can become syntactically invalid; if it expands to labels absent from a metric family, aggregation cardinality and legends can differ across panels.
- Several Titan duration panels have label/selector mismatches visible in this chunk: `Blob file read duration` labels the `percentile99` selector as `95%` and the `percentile95` selector as `99%`; `Blob file write duration` shows the same inversion. This can mislead latency diagnosis even if the underlying metrics are correct.
- Some panels group by `type` even while selecting a single exact `type` value. This is harmless but can make legends verbose and may retain stale type labels if metric naming changes.
- `topk(20)` on blob cache size hides lower-ranked instances/CFs. It is useful for dashboards but not complete enough for fleet-wide capacity accounting.
- `sum(increase(...[$__rate_interval])) by (le)` in the ingestion heatmap depends on bucket monotonicity and scrape continuity; resets or sparse ingestion can make the heatmap noisy.
- The chunk ends inside the next In Memory Engine panel (`The count of different types of region`), so this report cannot fully characterize that panel's target expressions.

## Test and Validation Signals

Useful checks for this dashboard chunk:

- JSON validity: the whole `tikv_details.json` should parse with `jq`; this was confirmed while extracting panel metadata.
- Panel coverage: expected visible IDs in this range are `263` through `314`, with rows `279` (`Titan - $titan_db`) and `307` (`In Memory Engine`).
- PromQL syntax validation: load the dashboard in Grafana against a Prometheus datasource and verify each target parses after variable expansion, especially expressions containing `$additional_groupby`.
- Metric availability: query Prometheus for every metric family listed above in a TiKV cluster with RocksDB, Titan, and in-memory engine features enabled.
- Semantic validation: compare `Blob file read duration` and `Blob file write duration` legend labels against their `type` selectors to fix the p95/p99 inversion if confirmed as unintended.
- Rendering validation: verify units match series semantics (`binBps` for byte flows, `bytes` for sizes, `ops` for operation rates, `s` for histogram seconds, and `microseconds` display for precomputed Titan micros metrics).
- Sparse-data validation: inspect ratio panels during no-traffic windows to ensure zero denominators do not create misleading alerts or unreadable legends.

## Chunk Boundaries and Merge Notes

This chunk starts in the middle of the RocksDB dashboard section after a preceding panel's axis configuration, then covers complete RocksDB panels `263` through `278`, the full Titan row `279` through `306`, and the start of In Memory Engine row `307` through panel `314`. The final per-file merge should combine this with adjacent chunks to recover the preceding RocksDB panels and the remaining In Memory Engine panel(s) after line `45105`.

### subset-b-008912: lines 45106-52917

# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 45106-52917

## Scope and Purpose

This chunk is a line-bounded slice of the TiKV Details Grafana dashboard JSON. It starts in the middle of panel `315` in the collapsed `In Memory Engine` row and ends inside panel `372` in the collapsed `Scheduler - $command` row. The file is declarative dashboard configuration, not executable source code, so the important "APIs" are Grafana panel schema fields, Prometheus/PromQL expressions, dashboard variables, and the TiKV metric series those expressions depend on.

The slice covers three operational areas:

- The tail of the `In Memory Engine` row, focused on cached region counts, cache GC/load/eviction/warmup, in-memory engine write and prepare-for-write latency, iterator seek/next/prev activity, per-region GC safe points, and auto-load/auto-evict decision distributions.
- Complete collapsed rows for `Flow Control`, `Scheduler`, and `Scheduler Worker Pool`, covering scheduler write/throttle flow, compaction pressure inputs, command queues, memory quota, YATP scheduler worker wait/execute latency, multilevel scheduling, and worker-pool task timing.
- The beginning of the `Scheduler - $command` row, covering command-specific stage totals, command duration, latch wait duration, key-read/key-write distributions, and the all-CF scan-detail panel for the selected `$command`.

Because the requested line range begins and ends inside panel objects, the final per-file report should reconcile this chunk with adjacent chunks before treating row boundaries as complete.

## Dashboard Structure

The chunk uses Grafana's legacy dashboard model:

- Rows are `type: "row"` panels with `collapsed: true` and a nested `panels` array.
- Graph panels use `type: "graph"`, legacy `xaxis`/`yaxes`, `renderer: "flot"`, right-side legend tables, and `nullPointMode: "null as zero"`.
- Heatmap panels use `type: "heatmap"`, `dataFormat: "tsbuckets"`, `format: "heatmap"` targets, hidden zero buckets, and bucket-axis units such as seconds or generic counts.
- Datasource references are `${DS_TEST-CLUSTER}` on child panels. Row containers have `datasource: null`.
- Most queries filter on `k8s_cluster="$k8s_cluster"`, `tidb_cluster="$tidb_cluster"`, and usually `instance=~"$instance"`.
- Many panels include `$additional_groupby` inside PromQL `by (...)` clauses and in legend templates; command-specific panels also use `$command`.

Panel groups in this chunk:

- `In Memory Engine` row `307`, panel IDs `315-336` within this slice.
- `Flow Control` row `337`, panel IDs `338-347`.
- `Scheduler` row `348`, panel IDs `349-356`.
- `Scheduler Worker Pool` row `357`, panel IDs `358-365`.
- `Scheduler - $command` row `366`, panel IDs `367-372` within this slice. The full row continues beyond this chunk in the source file.

## Important APIs, Types, and Query Functions

There are no application functions or Rust/Go types in this JSON. The operative interfaces are:

- Grafana panel fields: `id`, `title`, `description`, `type`, `datasource`, `targets`, `legend`, `seriesOverrides`, `gridPos`, `tooltip`, `fieldConfig`, `yaxes`, and heatmap `xAxis`/`yAxis`.
- PromQL range functions: `rate`, `increase`, `delta`, and `avg_over_time`.
- PromQL aggregations: `sum`, `avg`, and `max` with `by (...)` groupings.
- PromQL histogram handling: `histogram_quantile` over bucket rates, and `_sum / _count` average overlays.
- Grafana variables: `$__rate_interval`, `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$additional_groupby`, `$optional_quantile`, and `$command`.

Common query idioms:

- Heatmaps: `sum(increase(<metric>_bucket{...}[$__rate_interval])) by (le)`.
- Tail latency graphs: `histogram_quantile(0.9999, sum(rate(<metric>_bucket{...}[$__rate_interval])) by (le, ...))` and a matching `0.99` query.
- Average overlays: `sum(rate(<metric>_sum[...])) by (...) / sum(rate(<metric>_count[...])) by (...)`.
- Count overlays: `sum(rate(<metric>_count[...])) by (...)`, often hidden or transformed to the negative secondary axis.
- Gauges: direct `sum((metric{...})) by (...)`, `max((metric{...})) by (...)`, or booleanized gauges such as `!= 0`.

## In Memory Engine Metrics and Behavior

The in-memory engine panels expose the lifecycle of regions cached in TiKV's in-memory engine:

- `Region Count` uses `tikv_in_memory_engine_cache_count` averaged by `instance` and `type` to show the number and type mix of cached regions.
- `GC Filter` uses `tikv_in_memory_engine_gc_filtered` rates by filter `type` and `$additional_groupby` to show cache-GC filtering activity.
- `Region GC Duration`, `Region Load Duration`, and `Region Eviction Duration` are heatmaps from `*_duration_secs_bucket` metrics, tracking latency distributions for GC, load, and eviction work.
- `Region Load Count` and `Region Eviction Count` use `delta(..._count[$__rate_interval])`, which treats histogram counts as interval deltas rather than per-second rates. This makes the panels event-count oriented over the current range interval.
- `Region Warmup Count` uses `tikv_in_memory_engine_transfer_leader_warmup_total` to observe warmup activity after leader transfer or related cache warmup triggers.
- `Write duration` and `99% In-memory engine write duration per server` use `tikv_in_memory_engine_write_duration_seconds_*` to provide both cluster heatmap distribution and per-instance p99.99/p99/average/count overlays.
- `Prepare for write duration` and its per-server percentile graph mirror the write-duration panels for `tikv_in_memory_engine_prepare_for_write_duration_seconds_*`.
- `Iterator operations` breaks `tikv_in_memory_engine_locate` into `number_db_seek`, `number_db_seek_found`, `number_db_next`, `number_db_next_found`, `number_db_prev`, and `number_db_prev_found`.
- `Seek duration` uses `tikv_in_memory_engine_seek_duration_*` with `histogram_quantile(1)`, `$optional_quantile`, `0.95`, and average overlays. The `1` quantile is a bucket-bound approximation, not an exact maximum.
- `Oldest Auto GC SafePoint`, `Newest Auto GC SafePoint`, `Auto GC SafePoint Gap`, and `Auto GC SafePoint Gap With TiKV` expose per-region in-memory-engine GC safe point age and gap by dividing timestamp-or-TSO-like values by `2^18`.
- `Cached Region Coprocessor Requests`, `Cached Region MVCC Amplification`, `Top Region Coprocessor Requests`, and `Top Region MVCC Amplification` are heatmaps used to understand auto-load/auto-evict inputs for cached versus top regions.

These panels integrate TiKV's in-memory engine with Prometheus and Grafana as an operational feedback loop: operators can see whether regions are being loaded, evicted, or GCed too often; whether in-memory writes or prepare steps have long tails; whether iterator activity is dominated by misses; and whether GC safe point gaps are growing enough to retain MVCC history.

## Flow Control Metrics and Behavior

The `Flow Control` row describes TiKV scheduler flow-control pressure:

- `Scheduler flow` compares `tikv_scheduler_write_flow` with nonzero `tikv_scheduler_throttle_flow`, grouped by `instance`, to show actual write flow and active throttling.
- `Scheduler discard ratio` divides `tikv_scheduler_discard_ratio` by `10000000`, then renders it as a percent-unit graph by `type`.
- `Throttle duration` is a heatmap over `tikv_scheduler_throttle_duration_seconds_bucket`.
- `Scheduler throttled CF` booleanizes `tikv_scheduler_throttle_cf != 0` and labels series by `instance` and `cf`, making column-family throttling visible.
- `Flow controller actions` rates `tikv_scheduler_throttle_action_total` by action `type`, column family `cf`, and `$additional_groupby`.
- `Flush/L0 flow` compares `tikv_scheduler_l0_flow` and `tikv_scheduler_flush_flow` by `instance` and `cf`, plus total-by-instance overlays.
- `Flow controller factors` graphs `tikv_scheduler_l0`, `tikv_scheduler_memtable`, and `tikv_scheduler_l0_avg`, all maxed by `instance`.
- `Compaction pending bytes` shows RocksDB `tikv_engine_pending_compaction_bytes{db="kv"}` by `cf`, with a hidden scheduler-specific pending-compaction query divided by `10000000`.
- `Txn command throttled duration` and `Non-txn command throttled duration` rate `tikv_txn_command_throttle_time_total` and `tikv_non_txn_command_throttle_time_total` by `type`.

This row is an integration point between RocksDB storage pressure, TiKV scheduler flow-control policy, and user-visible command throttling. It lets operators correlate write flow, L0/memtable factors, pending compaction bytes, and throttle actions before moving to command-level scheduler panels.

## Scheduler Metrics and Behavior

The `Scheduler` row focuses on the transaction scheduler as a queueing and memory-governed subsystem:

- `Scheduler stage total` overlays `tikv_scheduler_too_busy_total` and `tikv_scheduler_stage_total` rates by `stage`, showing both normal command-stage throughput and too-busy rejections.
- `Scheduler priority commands` rates `tikv_scheduler_commands_pri_total` by command `priority`.
- `Scheduler pending commands` graphs `tikv_scheduler_contex_total` by `instance`. The metric name appears to be spelled `contex`, so renaming it would break this dashboard unless queries are migrated.
- `Scheduler running commands` graphs `tikv_scheduler_running_commands` by `instance`.
- `Scheduler writing bytes` graphs `tikv_scheduler_writing_bytes` by `instance`.
- `Scheduler memory quota` overlays `tikv_scheduler_memory_quota_size{type="in_use"}` and `{type="capacity"}` by `instance`.
- `Txn Scheduler Pool Wait Duration` and `Txn Scheduler Pool Exec Duration` are heatmaps over YATP scheduler-worker pool wait and exec bucket metrics filtered by `name=~"sched-worker.*"`.

These panels model the scheduler as a flow from queued command contexts, through running commands, to write bytes and memory quota. The YATP pool heatmaps connect scheduler symptoms to worker-pool saturation.

## Scheduler Worker Pool Metrics and Behavior

The `Scheduler Worker Pool` row tracks multilevel YATP scheduling behavior for `sched-worker.*` pools:

- `Time used by level` rates `tikv_multilevel_level_elapsed` by `level`, with level 0 described as small queries.
- `Level 0 chance` graphs `tikv_multilevel_level0_chance` per instance, indicating how often small tasks are selected.
- `Running tasks` uses `avg_over_time(tikv_scheduler_running_commands[1m])` by `instance` and `$additional_groupby`.
- `Wait Duration` duplicates the scheduler wait-duration heatmap for `tikv_yatp_pool_schedule_wait_duration_bucket`.
- `Running threads` uses `avg_over_time(tikv_unified_read_pool_thread_count[1m])`; despite the row being scheduler-worker oriented, this metric name references the unified read pool, so the panel should be checked for intentional reuse versus copy/paste drift.
- `Duration of One Time Slice` uses `tikv_yatp_task_poll_duration_*` p99.99, p99, average, and count overlays.
- `Task Execute Duration` uses `tikv_yatp_task_exec_duration_*`.
- `Task Schedule Times` uses `tikv_yatp_task_execute_times_*`.

This row is important when scheduler latency could come from worker-pool scheduling rather than storage or command semantics. The multilevel panels expose fairness and small-task preference, while poll/exec/schedule-times histograms expose per-task runtime and rescheduling behavior.

## Command-Specific Scheduler Metrics

The `Scheduler - $command` row starts at panel ID `366` and is parameterized by `$command`. Within this chunk it includes:

- `Scheduler stage total`, filtering `tikv_scheduler_too_busy_total` and `tikv_scheduler_stage_total` with `type="$command"`.
- `Scheduler command duration`, using `tikv_scheduler_command_duration_seconds_*` to show p99.99, p99, average, and hidden count for the selected command.
- `Scheduler latch wait duration`, using `tikv_scheduler_latch_wait_duration_seconds_*` to isolate latch contention within the selected command path.
- `Scheduler keys read`, using `tikv_scheduler_kv_command_key_read_*` to show key-read distribution and count.
- `Scheduler keys written`, using `tikv_scheduler_kv_command_key_write_*` to show key-write distribution and count.
- `Scheduler scan details`, using `tikv_scheduler_kv_scan_details{req="$command"}` by scan `tag` and `$additional_groupby`.

The chunk ends inside the `Scheduler scan details` panel after the `xaxis` block begins. Later panels in the same row, such as CF-specific scan details and command process/block-read duration, are outside this requested line range and must be handled by following chunks.

## State and Persistence Behavior

The JSON persists Grafana dashboard state only: row collapse state, panel IDs, panel layout, titles/descriptions, datasource variables, query strings, legend display state, axis units, heatmap options, and series overrides. It does not persist TiKV runtime state.

The persisted dashboard state does, however, encode assumptions about TiKV runtime state:

- In-memory engine state is observed through cached region counts, load/eviction/GC counters, safe point gauges, write/prepare histograms, and auto-load/auto-evict input distributions.
- Scheduler state is observed through command queues, running commands, memory quota in-use/capacity gauges, write bytes, flow-controller throttle status, and worker-pool histograms.
- Storage pressure state is observed indirectly through L0 flow, flush flow, memtable factors, and pending compaction bytes.
- Command-specific state is observed through `$command`-filtered stage counters, duration histograms, latch wait histograms, key read/write histograms, and scan-detail counters.

PromQL functions imply stateful metric semantics. `rate` and `increase` assume counter-like monotonicity; `delta` assumes meaningful changes over the selected range; `avg_over_time` depends on scrape continuity; histogram quantiles assume bucket label `le` and complete bucket series. Counter resets, missing scrapes, or metric-label churn can therefore look like real TiKV behavior in these panels.

## Dependencies and Integration Points

Primary dependencies:

- Grafana legacy graph, heatmap, and row panel schema.
- Prometheus datasource `${DS_TEST-CLUSTER}`.
- Grafana runtime variables `$__rate_interval`, `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$additional_groupby`, `$optional_quantile`, and `$command`.
- TiKV Prometheus exporters for in-memory engine, scheduler, flow control, RocksDB engine, YATP, multilevel scheduler, and unified read/scheduler pool metrics.

Operational integration points:

- In-memory-engine panels support debugging cache churn, region warmup, safe point lag, write-path overhead, and auto-load/auto-evict decisions.
- Flow-control panels support debugging throttling from L0, memtable, flush, and compaction pressure.
- Scheduler panels support transaction scheduler queue, memory, write-size, too-busy, and worker-pool diagnosis.
- Command-specific panels support isolating latency, latch waits, and read/write/scan amplification for a selected command such as commit.

## Risks and Edge Cases

- The chunk starts mid-panel and ends mid-panel. Any automated reader of this line range alone does not see complete JSON objects for the first and last panels.
- `$additional_groupby` appears inside many `by (...)` clauses. If it expands to an empty string or an invalid comma-separated fragment, PromQL syntax can break or grouping can change unexpectedly.
- `$command` is embedded as an exact label match in some panels with `type="$command"` and as `req="$command"` in scan details. Dashboard variable values must match TiKV label values exactly.
- `nullPointMode: "null as zero"` can hide missing data, scrape gaps, or removed metric series by rendering them as zeros.
- High-cardinality labels such as `instance`, `cf`, `type`, `tag`, `priority`, `level`, and arbitrary `$additional_groupby` values can make histogram quantile and heatmap queries expensive.
- Several panels use p99.99 histograms. These are sensitive to sparse bucket data and scrape interval selection.
- `histogram_quantile(1, ...)` in `Seek duration` should be interpreted as the highest observed bucket boundary estimate, not a precise maximum.
- The in-memory load and eviction count panels use `delta` on histogram count series instead of `rate` or `increase`; this may behave poorly around counter resets.
- Some axis scaling is manual: safe points divide by `2^18`, discard ratio divides by `10000000`, and one hidden pending-compaction query divides by `10000000`. These constants should be verified against the metric units before changing.
- `Scheduler pending commands` references `tikv_scheduler_contex_total`; this likely preserves an existing exported metric spelling. Correcting the spelling in only the dashboard would break the panel.
- `Running threads` in the scheduler worker row uses `tikv_unified_read_pool_thread_count` while the rest of the row filters `sched-worker.*`. This may be intentional cross-pool context or a dashboard drift risk.

## Test Signals

Useful validation is dashboard and query validation rather than unit testing:

- Parse the complete `tikv_details.json` with `jq` to ensure the source file is still valid JSON after any dashboard edits.
- Import or provision the dashboard into Grafana to catch legacy panel schema issues, duplicate panel IDs, broken row nesting, invalid datasource references, and bad heatmap/graph rendering.
- Substitute representative values for `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$additional_groupby`, `$optional_quantile`, and `$command`, then validate the resulting PromQL expressions against Prometheus.
- Check that all referenced metric families exist in TiKV `/metrics`, including `_bucket`, `_sum`, and `_count` siblings for histogram panels.
- Smoke-test both empty and non-empty `$additional_groupby` configurations because it is used in many group-by clauses.
- Verify heatmap panels render bucket distributions with the expected units and that graph legends hide or show average/count overlays as intended.
- Compare scheduler worker panels against live worker-pool metrics to confirm `sched-worker.*` filters and the `tikv_unified_read_pool_thread_count` panel are intentional.

## Cross-Chunk Notes

This chunk should be merged with adjacent chunks for complete panel context:

- The beginning of panel `315` and earlier `In Memory Engine` panels are before line `45106`.
- The `Scheduler scan details` panel `372` continues after line `52917`.
- The remainder of the `Scheduler - $command` row, including CF-specific scan details and later command-processing panels, is outside this work item.

### subset-b-008913: lines 52918-60535

# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 52918-60535

## Scope and Purpose

This chunk is a contiguous slice of the TiKV Details Grafana dashboard JSON. It is declarative observability configuration, not executable TiKV code, so the relevant "APIs" are Grafana panel fields, PromQL expressions, dashboard variables, panel IDs, row layout, and the TiKV/TiDB metrics those expressions bind to.

The slice starts near the end of a collapsed Scheduler row, covers complete collapsed rows for Coprocessor Overview, Coprocessor Detail, and Unified Read Pool, then covers most of the beginning of the GC row before ending inside the next panel definition. Its purpose is to visualize read-path and GC behavior: scheduler scan details and scheduler latency for a selected `$command`, coprocessor request latency, request volume, scan-key and RocksDB perf detail, coprocessor memory/semaphore pressure, YATP unified-read-pool scheduling, GC worker throughput/failures/duration, TiDB GC progress/configuration, TiKV auto-GC progress/safepoint, and GC compaction-filter activity.

## Dashboard Structure and Panels

- Scheduler continuation: `Scheduler scan details [lock]`, `[write]`, and `[default]` query `tikv_scheduler_kv_scan_details` by `tag` for each CF with `req="$command"`; `Scheduler command process duration` and `Scheduler command block read duration` use p99.99, p99, average, and hidden count overlays from scheduler histogram families; `Check memory locks duration` is a heatmap over `tikv_storage_check_mem_lock_duration_seconds_bucket`.
- `Coprocessor Overview` row: starts at row id 379 and contains request-duration heatmap and percentile graph, total request rate, request errors, cursor/scan-key operations, RocksDB perf statistics, response bytes, and coprocessor memory quota. These panels use `tikv_coprocessor_request_duration_seconds_*`, `tikv_coprocessor_request_error`, `tikv_coprocessor_scan_keys_*`, `tikv_coprocessor_rocksdb_perf`, `tikv_coprocessor_response_bytes`, and `tikv_coprocessor_memory_quota`.
- `Coprocessor Detail` row: starts at row id 389 and breaks coprocessor work into handle duration, handle duration by store, wait duration, wait duration by store, DAG request/executor counters, table/index scan details with and without CF grouping, memory-lock-check heatmap and percentile graph, semaphore wait heatmap and percentile graph, and current semaphore waiting task count.
- `Unified Read Pool` row: starts at row id 405 and tracks the YATP/unified-read pool using `tikv_multilevel_level_elapsed`, `tikv_multilevel_level0_chance`, `tikv_unified_read_pool_running_tasks`, `tikv_yatp_pool_schedule_wait_duration_bucket`, `tikv_unified_read_pool_thread_count`, `tikv_yatp_task_poll_duration_*`, `tikv_yatp_task_exec_duration_*`, and `tikv_yatp_task_execute_times_*`.
- `GC` row: starts at row id 414 and includes complete panels for GC tasks, GC task duration, TiDB GC seconds, TiDB GC worker actions, ResolveLocks progress, TiKV auto-GC progress, GC speed, TiKV auto-GC safepoint, GC lifetime, GC interval, and GC in compaction filter. The chunk ends after the opening fields of panel id 426, `GC scan write details`, so that panel's targets and behavior are not fully present here.

Most panels use Grafana legacy `graph`, `heatmap`, `stat`, and collapsed `row` schemas. Graph panels generally set a right-side legend table, hide empty/zero series, sort by maximum descending, render with flot, and use `nullPointMode: "null as zero"`. Heatmap panels use `dataFormat: "tsbuckets"`, hide zero buckets, and plot bucket upper bounds on the Y axis. Stat panels use `lastNotNull` reduction for the GC lifetime and interval configuration values.

## Important Query Patterns

- Histogram heatmaps use `sum(increase(<metric>_bucket{...}[$__rate_interval])) by (le)` and `format: "heatmap"`. This appears in scheduler memory-lock checks, coprocessor request duration, coprocessor memory-lock checks, semaphore waiting duration, and unified-read-pool schedule wait.
- Percentile latency graphs use `histogram_quantile(0.9999, ...)` and `histogram_quantile(0.99, ...)` over `sum(rate(<metric>_bucket{...}[$__rate_interval])) by (..., le, $additional_groupby)`. The same panels usually add average overlays as `rate(_sum) / rate(_count)` and hidden count overlays from `_count`.
- Counter/rate panels use `sum(rate(metric{...}[$__rate_interval])) by (...)`, for example request totals, request errors, DAG requests/executors, scheduler scan details, GC task counters, TiDB GC worker actions, GC speed, and GC compaction filter counters.
- Gauge/config panels use direct aggregation without `rate`, such as `sum(tikv_coprocessor_memory_quota)`, `tikv_multilevel_level0_chance`, `avg_over_time` for running task/thread counts, `max(tidb_tikvclient_range_task_stats)`, and `max(tidb_tikvclient_gc_config)`.
- Nearly every query filters by `k8s_cluster="$k8s_cluster"` and `tidb_cluster="$tidb_cluster"`; most TiKV-side panels also filter `instance=~"$instance"`. Scheduler and GC-duration panels additionally depend on `$command`; many panels inject `$additional_groupby` into both `by (...)` clauses and legend templates.

## Metrics Covered

Scheduler metrics:

- `tikv_scheduler_kv_scan_details`
- `tikv_scheduler_processing_read_duration_seconds_bucket`, `_sum`, `_count`
- `tikv_scheduler_block_read_duration_seconds_bucket`, `_sum`, `_count`
- `tikv_storage_check_mem_lock_duration_seconds_bucket`

Coprocessor overview/detail metrics:

- `tikv_coprocessor_request_duration_seconds_bucket`, `_sum`, `_count`
- `tikv_coprocessor_request_error`
- `tikv_coprocessor_scan_keys_bucket`, `_sum`, `_count`
- `tikv_coprocessor_rocksdb_perf`
- `tikv_coprocessor_response_bytes`
- `tikv_coprocessor_memory_quota`
- `tikv_coprocessor_request_handle_seconds_bucket`, `_sum`, `_count`
- `tikv_coprocessor_request_wait_seconds_bucket`, `_sum`, `_count`
- `tikv_coprocessor_dag_request_count`
- `tikv_coprocessor_executor_count`
- `tikv_coprocessor_scan_details`
- `tikv_coprocessor_mem_lock_check_duration_seconds_bucket`, `_sum`, `_count`
- `tikv_coprocessor_semaphore_wait_time_duration_seconds_bucket`, `_sum`, `_count`
- `tikv_coprocessor_waiting_for_semaphore`

Unified read pool metrics:

- `tikv_multilevel_level_elapsed`
- `tikv_multilevel_level0_chance`
- `tikv_unified_read_pool_running_tasks`
- `tikv_yatp_pool_schedule_wait_duration_bucket`
- `tikv_unified_read_pool_thread_count`
- `tikv_yatp_task_poll_duration_bucket`, `_sum`, `_count`
- `tikv_yatp_task_exec_duration_bucket`, `_sum`, `_count`
- `tikv_yatp_task_execute_times_bucket`, `_sum`, `_count`

GC and TiDB/TiKV GC metrics:

- `tikv_gcworker_gc_tasks_vec`
- `tikv_storage_gc_skipped_counter`
- `tikv_gcworker_gc_task_fail_vec`
- `tikv_gc_worker_too_busy`
- `tikv_gcworker_gc_task_duration_vec_bucket`, `_sum`, `_count`
- `tidb_tikvclient_gc_seconds_bucket`
- `tidb_tikvclient_gc_worker_actions_total`
- `tidb_tikvclient_range_task_stats`
- `tikv_gcworker_autogc_processed_regions`
- `tikv_raftstore_region_count`
- `tikv_storage_mvcc_gc_delete_versions_sum`
- `tikv_gcworker_autogc_safe_point`
- `tidb_tikvclient_gc_config`
- `tikv_gc_compaction_filtered`
- `tikv_gc_compaction_filter_skip`
- `tikv_gc_compaction_mvcc_rollback`
- `tikv_gc_compaction_filter_orphan_versions`
- `tikv_gc_compaction_filter_perform`
- `tikv_gc_compaction_failure`
- `tikv_gc_compaction_filter_mvcc_deletion_met`
- `tikv_gc_compaction_filter_mvcc_deletion_handled`
- `tikv_gc_compaction_filter_mvcc_deletion_wasted`

## Control Flow and Observability Model

Grafana evaluates this JSON by row and panel. Collapsed rows keep their child panel definitions inside a row-level `panels` array; expanding a row causes the child panel targets to run against `${DS_TEST-CLUSTER}` with the current dashboard variable substitutions.

The implicit diagnostic flow is:

1. Scheduler panels show how the selected scheduler `$command` interacts with RocksDB CF scans, command processing latency, block-read latency, and memory-lock checks.
2. Coprocessor overview panels provide a broad read-path view: request duration distribution, request throughput, errors, scan-key/cursor volume, RocksDB internal delete-skip perf statistics, response size, and memory quota.
3. Coprocessor detail panels separate service time from queue/wait time. They distinguish total handle duration, per-store handle duration, request wait duration, per-store wait duration, DAG request/executor mix, table/index scan operations, memory-lock-check latency, semaphore wait latency, and currently waiting semaphore tasks.
4. Unified read pool panels correlate coprocessor/read workload with YATP scheduling: level elapsed time, level-0 scheduling chance for small tasks, running tasks, schedule wait heatmap, running threads, time-slice duration, total task execution duration, and number of scheduling slices per task.
5. GC panels move from worker throughput and duration to TiDB GC orchestration, ResolveLocks progress, TiKV auto-GC progress, safe point/configuration, GC speed, and compaction-filter behavior.

This chunk intentionally combines distribution panels with attribution panels. Heatmaps show bucket shape over time, while graph panels preserve `instance`, `req`, `task`, `type`, `key_mode`, `cf`, `tag`, `priority`, or `$additional_groupby` labels for drilldown.

## State and Persistence Behavior

The JSON persists Grafana dashboard state only: panel IDs, row collapse state, grid coordinates, datasource references, query strings, legend/axis/tooltip behavior, stat reductions, and variable placeholders. It does not persist TiKV state or mutate Prometheus data.

The observed runtime state is external and time-series based. Scheduler, coprocessor, unified-read-pool, and GC components emit metrics; Prometheus scrapes them; Grafana queries them with `rate`, `increase`, `avg_over_time`, and direct aggregation. Counter semantics and scrape continuity matter because most rate panels assume monotonic counters, while histogram panels assume complete `_bucket`, `_sum`, and `_count` families with stable bucket labels.

Persistence-related behavior is visible through GC and MVCC panels rather than through local storage writes in this JSON. `tikv_storage_mvcc_gc_delete_versions_sum`, GC compaction filter counters, `tikv_gcworker_autogc_safe_point`, `tidb_tikvclient_gc_config`, and TiDB GC worker metrics expose how MVCC versions are retained or removed and how GC safe-point/configuration state affects storage cleanup. The chunk also shows `tikv_raftstore_region_count` used as the denominator for TiKV auto-GC progress, tying GC progress to persisted region inventory.

## Dependencies and Integration Points

- Grafana legacy dashboard schema: collapsed `row` panels, `graph`, `heatmap`, `stat`, `targets`, `seriesOverrides`, `fieldConfig`, `gridPos`, legends, axes, and tooltips.
- Prometheus datasource variable `${DS_TEST-CLUSTER}` and Grafana interval variable `$__rate_interval`.
- Dashboard variables: `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$command`, and `$additional_groupby`.
- TiKV metrics exporters for scheduler, storage lock checks, coprocessor, YATP/unified read pool, raftstore region counts, GC worker, MVCC GC, and GC compaction filter metrics.
- TiDB metrics exporters for `tidb_tikvclient_gc_seconds_bucket`, `tidb_tikvclient_gc_worker_actions_total`, `tidb_tikvclient_range_task_stats`, and `tidb_tikvclient_gc_config`.
- Operational integration with TiKV/TiDB troubleshooting: read latency, read queuing, coprocessor executor mix, memory lock contention, semaphore throttling, thread-pool saturation, GC worker saturation, GC safe-point drift, and compaction-filter health.

## Risks and Edge Cases

- `$additional_groupby` is inserted directly into `by (...)` clauses. Empty, malformed, or comma-prefixed substitutions can break PromQL or silently alter aggregation semantics.
- Several high-cardinality dimensions can be combined: `instance`, `req`, `tag`, `cf`, `type`, `task`, `key_mode`, `priority`, and `$additional_groupby`. Histogram quantiles over these labels, especially p99.99, can be expensive on large clusters.
- Many graph panels use `nullPointMode: "null as zero"`. Missing scrapes or missing label series can look like real zeros.
- Average expressions divide `_sum` rates by `_count` rates. If the denominator is zero or absent, panels can show gaps, infinities, or misleading drops depending on Grafana/Prometheus behavior.
- The scheduler and GC-duration panels use `$command`, but the row titles around this chunk are mixed: scheduler panels are under `Scheduler - $command`, while the GC task duration panel also filters `type="$command"`. Variable values that make sense for scheduler commands may not make sense for GC task types.
- The `TiDB GC seconds` panel uses `histogram_quantile(1, ...)`, which estimates the upper histogram bucket boundary rather than an exact maximum duration.
- `TiKV Auto GC SafePoint` divides `tikv_gcworker_autogc_safe_point` by `2^18` and formats it as `dateTimeAsIso`; this assumes the metric encodes a TiDB/TiKV timestamp whose physical time is recovered by that conversion.
- `TiKV Auto GC Progress` divides auto-GC processed regions by raftstore region count per instance. If the numerator and denominator are scraped at different moments or labels differ, progress can spike or be absent.
- The chunk ends at line 60535 inside panel id 426, `GC scan write details`; the targets and final rendering options for that panel must be recovered from the next chunk before a complete per-file report is assembled.

## Test Signals

Because this is dashboard JSON, validation should focus on configuration and query behavior:

- Parse the full `tikv_details.json` as JSON after any edit to ensure row nesting and comma boundaries remain valid.
- Import or provision the dashboard in Grafana to catch duplicate panel IDs, invalid legacy graph/heatmap/stat fields, broken datasource variables, and malformed row collapse state.
- Substitute representative dashboard variables and validate PromQL expressions with Prometheus query APIs or a promtool-like checker, especially expressions containing `$additional_groupby` and `$command`.
- Verify the referenced metric families exist in TiKV and TiDB `/metrics` output, including histogram `_bucket`, `_sum`, and `_count` siblings.
- Smoke-test with several variable combinations: all instances, a single `$instance`, no extra group-by, grouping by `instance`, grouping by `req`, grouping by `task`, and grouping by `key_mode`.
- Visually inspect heatmaps and graph legends in Grafana to confirm bucket formats, date-time safepoint conversion, negative-Y count overlays, hidden count series, and stat `lastNotNull` reductions render as intended.

## Cross-Chunk Notes

This work item starts mid-dashboard after earlier scheduler panels and ends inside the opening of `GC scan write details` panel id 426. The final merged per-file research should combine this chunk with adjacent chunks to recover the full scheduler row before line 52918, the remainder of panel id 426 after line 60535, later GC panels, dashboard templating definitions, and top-level dashboard metadata.

### subset-b-008914: lines 60536-68613

# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 60536-68613

## Scope and Purpose

This chunk is a contiguous slice of the TiKV Details Grafana dashboard JSON. It starts inside the `GC scan write details` panel and continues through the rest of the visible GC/auto-compaction panels, the complete `Pessimistic Locking`, `Task`, `PD`, `Slow Trend Statistics`, and `Snapshot` rows, then enters the `Resolved TS` row and ends at the beginning of the `Max gap of resolved-ts in region leaders` panel. The file is declarative Grafana dashboard configuration, so the important interfaces are panel objects, row nesting, Prometheus expressions, Grafana dashboard variables, and TiKV metric names.

Operationally, this chunk covers observability for several TiKV subsystems:

- GC and auto compaction: GC scan keys by CF, auto-compaction latency, candidate counts, tombstone/discardable-version distributions, MVCC versions scanned, and compaction score.
- Pessimistic locking: lock-manager worker CPU, handled tasks, waiter lifetime, wait-table and wait-queue gauges, deadlock detection, detector leadership, pessimistic-lock memory, in-memory lock result rates, queue length heatmap, and MVCC scan-lock read duration.
- Generic task pools: worker and future-pool handled/pending task panels.
- PD client behavior: request counts, average request duration, heartbeats, peer validation, reconnects, forward status, and pending TSO requests.
- Slow-store trend signals: raftstore inspect duration, store slow score, disk probe duration, slow trend, QPS trend, sampling latency, and current QPS by instance.
- Snapshot path: snapshot message rate, state counts, generation/apply wait, handle duration, p99.99 size/KV count, snapshot actions, transport/generate speed, and pending applies.
- Resolved TS start: worker CPU and the first gap/region panels for resolved-ts and follower safe-ts.

## Dashboard Structure and Panels

The chunk uses the legacy Grafana `graph`, `heatmap`, and collapsed `row` schema. Most graphs use `${DS_TEST-CLUSTER}` as datasource, `renderer: "flot"`, `nullPointMode: "null as zero"`, right-side legend tables sorted by `max`, and `hideEmpty`/`hideZero` enabled. The dashboard variables repeated in nearly every PromQL target are `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$__rate_interval`, `$additional_groupby`, and, for selected percentile panels, `$optional_quantile`.

Panel coverage in this slice:

- GC tail and auto compaction:
  - `GC scan write details` and `GC scan default details` query `tikv_gcworker_gc_keys` for `cf="write"` and `cf="default"`, grouped by `key_mode`, `tag`, and `$additional_groupby`.
  - `Auto Compaction Duration` has p99.99, p99, average, and count targets over `tikv_auto_compaction_duration_seconds_*`, grouped by `type`.
  - `Auto Compaction Regions Status` directly sums `tikv_auto_compaction_regions_meet_threshold` and `tikv_auto_compaction_pending_candidates` by `instance`.
  - `Auto Compaction Num Tombstones`, `Auto Compaction Num Discardable`, `Auto Compaction MVCC Versions Scanned`, and `Auto Compaction Score` repeat the p99.99/p99/avg/count histogram pattern over their corresponding `_bucket`, `_sum`, and `_count` metrics.
- `Pessimistic Locking` row:
  - `Lock Manager Thread CPU` tracks `waiter_manager.*` and `deadlock_detect.*` thread CPU with `tikv_thread_cpu_seconds_total`.
  - `Lock Manager Handled tasks` uses `tikv_lock_manager_task_counter` by `type`.
  - `Waiter lifetime duration` and `Deadlock detect duration` use p99.99, p99, average, and count targets over lock-manager duration histograms.
  - `Lock Waiting Queue` compares `tikv_lock_manager_wait_table_status` and `tikv_lock_wait_queue_entries_gauge_vec` using `max_over_time(...[30s])`.
  - `Detect error`, `Deadlock detector leader`, `Total pessimistic locks memory size`, `In-memory pessimistic locking result`, and `Pessimistic lock activities` expose error counters, detector leadership heartbeat, memory gauge, result rates, and active key/waiter gauges.
  - `Lengths of lock wait queues when transaction enqueues` is the only heatmap in this chunk; it uses `sum(increase(tikv_lock_wait_queue_length_bucket[$__rate_interval])) by (le)`.
  - `In-memory scan lock read duration` uses histogram percentiles, average, and count over `tikv_storage_mvcc_scan_lock_read_duration_seconds_*`, grouped by `type`.
- `Task` row:
  - `Worker handled tasks` and `Worker pending tasks` expose `tikv_worker_handled_task_total` rates and `tikv_worker_pending_task_total` gauges by worker `name`.
  - `FuturePool handled tasks` and `FuturePool pending tasks` mirror the worker panels with `tikv_futurepool_handled_task_total` and `tikv_futurepool_pending_task_total`; pending future-pool tasks use `avg_over_time(...[1m])`.
- `PD` row:
  - `PD requests` and `PD request duration (average)` use `tikv_pd_request_duration_seconds_count` and `_sum/_count` average by request `type`.
  - `PD heartbeats` combines `tikv_pd_heartbeat_message_total` rates with direct pending heartbeat gauge `tikv_pd_pending_heartbeat_total`.
  - `PD validate peers`, `PD reconnection`, `PD forward status`, and `Pending TSO Requests` query peer validation counters, reconnect deltas, forwarding status, and TSO queue gauges.
- `Slow Trend Statistics` row:
  - `Inspected duration per server` and `Disk Probe Duration` use `$optional_quantile` over raftstore inspect and disk probe histograms.
  - `Store Slow Score`, `Slow Trend`, `QPS Changing Trend`, `AVG Sampling Latency`, and `QPS of each store` directly sum slow-score/trend gauge metrics by `instance`.
- `Snapshot` row:
  - `Rate snapshot message` uses a 1-minute `delta` of `tikv_raftstore_raft_sent_message_total{type="snapshot"}`.
  - `Snapshot state count` combines `tikv_raftstore_snapshot_traffic_total` and `tikv_pending_delete_ranges_of_stale_peer`.
  - `Snapshot generation/apply wait duration $optional_quantile` and `Handle snapshot duration $optional_quantile` use histogram quantiles over generation, apply, send, and snapshot duration buckets.
  - `99.99% Snapshot size` and `99.99% Snapshot KV count` use fixed p99.99 quantiles.
  - `Snapshot Actions` uses 1-minute deltas for `tikv_raftstore_snapshot_total`, `tikv_raftstore_clean_region_count`, and `tikv_server_snapshot_task_total`.
  - `Snapshot transport speed` measures `tikv_snapshot_limit_transport_bytes` for non-send transport types and `tikv_snapshot_limit_generate_bytes` for `type=~"io"`.
  - `Snapshot pending applies` directly displays `tikv_raftstore_snapshot_pending_applies`.
- `Resolved TS` row start:
  - `Resolved TS Worker CPU`, `Advance ts Worker CPU`, and `Scan lock Worker CPU` use `tikv_thread_cpu_seconds_total` filtered by thread-name regexes `resolved_ts.*`, `advance_ts.*`, and `inc_scan.*`.
  - `Max gap of resolved-ts`, `Min Resolved TS Region`, `Max gap of follower safe-ts`, and `Min Safe TS Follower Region` display resolved-ts/safe-ts lag and region gauges by `instance`.
  - The chunk ends just as `Max gap of resolved-ts in region leaders` begins, so only its title/description and opening object fields are visible in this work item.

## Important Query Patterns and Data Contracts

Histogram percentile panels use:

- `histogram_quantile(0.9999, sum(rate(<metric>_bucket{...}[$__rate_interval])) by (..., le, $additional_groupby))` for fixed p99.99 lines.
- `histogram_quantile(0.99, ...)` for p99 lines in auto-compaction and lock-manager panels.
- `histogram_quantile($optional_quantile, ...)` for operator-selected quantiles in slow-trend and snapshot panels.

Average panels use the conventional Prometheus histogram average formula:

- `sum(rate(<metric>_sum{...}[$__rate_interval])) by (...) / sum(rate(<metric>_count{...}[$__rate_interval])) by (...)`.

Counter-rate panels use `sum(rate(...[$__rate_interval])) by (...)`. Snapshot action and reconnect panels use `delta(...[1m])` or `delta(...[$__rate_interval])`; these are sensitive to counter reset behavior. Gauge panels usually use direct `sum((metric{...})) by (...)`, while queue status panels use `max_over_time(...[30s])` to smooth short-lived lock-manager state.

`$additional_groupby` is interpolated into many `by (...)` clauses and legend templates. It is an important integration contract: the variable must expand to a syntactically valid PromQL label list in contexts such as `by (type, $additional_groupby)`, `by ($additional_groupby)`, and `legendFormat` strings like `{{$additional_groupby}}`.

## Metrics Covered

Metrics referenced by this chunk include:

- GC and auto compaction: `tikv_gcworker_gc_keys`, `tikv_auto_compaction_duration_seconds_*`, `tikv_auto_compaction_regions_meet_threshold`, `tikv_auto_compaction_pending_candidates`, `tikv_auto_compaction_num_tombstones_*`, `tikv_auto_compaction_num_discardable_*`, `tikv_auto_compaction_mvcc_versions_scanned_*`, and `tikv_auto_compaction_score_*`.
- Lock manager and pessimistic locking: `tikv_thread_cpu_seconds_total`, `tikv_lock_manager_task_counter`, `tikv_lock_manager_waiter_lifetime_duration_*`, `tikv_lock_manager_wait_table_status`, `tikv_lock_wait_queue_entries_gauge_vec`, `tikv_lock_manager_detect_duration_*`, `tikv_lock_manager_error_counter`, `tikv_lock_manager_detector_leader_heartbeat`, `tikv_pessimistic_lock_memory_size`, `tikv_in_memory_pessimistic_locking`, `tikv_lock_wait_queue_length_bucket`, and `tikv_storage_mvcc_scan_lock_read_duration_seconds_*`.
- Generic workers: `tikv_worker_handled_task_total`, `tikv_worker_pending_task_total`, `tikv_futurepool_handled_task_total`, and `tikv_futurepool_pending_task_total`.
- PD client: `tikv_pd_request_duration_seconds_*`, `tikv_pd_heartbeat_message_total`, `tikv_pd_pending_heartbeat_total`, `tikv_pd_validate_peer_total`, `tikv_pd_reconnect_total`, `tikv_pd_request_forwarded`, and `tikv_pd_pending_tso_request_total`.
- Slow trend: `tikv_raftstore_inspect_duration_seconds_bucket`, `tikv_raftstore_slow_score`, `tikv_raftstore_disk_probe_duration_seconds_bucket`, `tikv_raftstore_slow_trend`, `tikv_raftstore_slow_trend_result`, `tikv_raftstore_slow_trend_l0`, and `tikv_raftstore_slow_trend_result_value`.
- Snapshot: `tikv_raftstore_raft_sent_message_total`, `tikv_raftstore_snapshot_traffic_total`, `tikv_pending_delete_ranges_of_stale_peer`, `tikv_raftstore_snapshot_generation_wait_duration_seconds_bucket`, `tikv_raftstore_snapshot_apply_wait_duration_seconds_bucket`, `tikv_server_send_snapshot_duration_seconds_bucket`, `tikv_raftstore_snapshot_duration_seconds_bucket`, `tikv_snapshot_size_bucket`, `tikv_snapshot_kv_count_bucket`, `tikv_raftstore_snapshot_total`, `tikv_raftstore_clean_region_count`, `tikv_server_snapshot_task_total`, `tikv_snapshot_limit_transport_bytes`, `tikv_snapshot_limit_generate_bytes`, and `tikv_raftstore_snapshot_pending_applies`.
- Resolved TS start: `tikv_resolved_ts_min_resolved_ts_gap_millis`, `tikv_resolved_ts_min_resolved_ts_region`, `tikv_resolved_ts_min_follower_safe_ts_gap_millis`, `tikv_resolved_ts_min_follower_safe_ts_region`, and the next chunk's visible continuation for `tikv_resolved_ts_min_leader_resolved_ts_gap_millis`.

## Control Flow and Observability Model

There is no executable control flow in this JSON. Grafana interprets the declarative object tree: collapsed row panels hold child `panels`, child panels run their `targets`, Prometheus evaluates the expressions after dashboard variable substitution, and Grafana renders the returned time series using graph or heatmap settings.

The implicit diagnostic flow in this chunk is:

1. Confirm GC scan and auto-compaction behavior. The GC panels separate `write` and `default` column families, while auto-compaction panels correlate duration with candidate volume, tombstone count, discardable versions, MVCC scan depth, and score.
2. Inspect pessimistic-locking pressure. CPU, task, queue, waiter-lifetime, deadlock-detection, memory, and in-memory-locking panels distinguish high lock contention from lock-manager scheduling, deadlock detector, or MVCC scan-lock read costs.
3. Check generic asynchronous task pressure. Worker and future-pool handled/pending panels indicate whether TiKV background pools are falling behind by worker/future-pool name.
4. Check PD client health. Request rate and average duration expose client-side PD latency; heartbeats, reconnects, forward status, validation, and pending TSO requests expose PD communication and TSO backpressure.
5. Identify slow-store trends. Slow score, disk probe duration, QPS trend, sampling latency, and QPS by instance provide a store-level signal that can explain Raftstore or PD-facing symptoms.
6. Investigate snapshot pressure. Snapshot state, wait, handling duration, size, KV count, action rates, transport/generate throughput, and pending applies identify whether snapshot generation, transfer, apply, or cleanup is contributing to lag.
7. Begin resolved-ts diagnosis. CPU and lag/region panels identify whether resolved-ts advancement is delayed and which regions/instances are responsible; this row continues in the next chunk.

The dashboard intentionally mixes high-percentile histograms, average/count overlays, direct gauges, and queue heatmaps. This gives operators a path from aggregate symptoms to per-instance attribution, but correctness depends on metric label stability and dashboard-variable expansion.

## State and Persistence Behavior

This chunk persists dashboard state only: panel IDs, row placement, row child membership, grid positions, descriptions, legends, tooltip behavior, axis units, datasource references, query strings, hidden/visible target flags, and variable placeholders. It does not persist TiKV runtime state. Runtime state is externalized through Prometheus time series scraped from TiKV.

The observed state includes both durable and transient operational state:

- Durable/persistent subsystem behavior is inferred from snapshot generation/apply, GC, compaction, and resolved-ts metrics.
- Transient queue and leadership state is inferred from lock waiting queues, detector heartbeat, worker/future-pool pending gauges, PD pending heartbeats, pending TSO requests, and snapshot pending applies.
- Counter-derived panels depend on Prometheus scrape history and monotonic counters; missing scrapes, restarts, or counter resets can create gaps or misleading `rate`, `increase`, or `delta` outputs.

Because many panels set `nullPointMode` to `null as zero` and hide empty/zero series, missing metrics can be visually quiet. That is helpful for sparse subsystems but risky when a missing exporter, renamed metric, or failed scrape should be visible as missing data rather than zero activity.

## Dependencies and Integration Points

- Grafana legacy dashboard schema: `row`, `graph`, `heatmap`, `gridPos`, `targets`, `legend`, `seriesOverrides`, `tooltip`, `xaxis`/`yaxes`, heatmap `dataFormat`, and datasource interpolation.
- Prometheus datasource `${DS_TEST-CLUSTER}` and PromQL functions `rate`, `increase`, `delta`, `avg_over_time`, `max_over_time`, `sum`, and `histogram_quantile`.
- Dashboard variables `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$additional_groupby`, `$optional_quantile`, and `$__rate_interval`.
- TiKV metrics exporters for GC worker, auto compaction, lock manager, in-memory pessimistic locking, worker/future pools, PD client, raftstore slow-trend detection, snapshot handling, and resolved-ts workers.
- Operational integration points include TiKV GC/compaction tuning, pessimistic transaction contention diagnosis, PD client and TSO troubleshooting, slow-store detection, snapshot backpressure analysis, and resolved-ts lag debugging.

## Risks and Edge Cases

- The chunk starts mid-panel. The opening `GC scan write details` panel is complete enough to recover its target, title, axes, and legend behavior, but final merged research should reconcile its object start from the previous chunk.
- The chunk ends inside panel 486. `Max gap of resolved-ts in region leaders` is only partially visible here; the next chunk must provide the target expression, legend, axes, and closing object.
- `$additional_groupby` appears inside `by ($additional_groupby)` and appended label lists. An empty or comma-prefixed/comma-suffixed expansion can make PromQL invalid unless the dashboard variable is configured carefully.
- High-cardinality labels can make several queries expensive: `type`, `result`, `status`, `disk`, `outcome`, `instance`, `name`, `key_mode`, `tag`, and arbitrary `$additional_groupby` values are used on histogram and rate aggregations.
- p99.99 and `$optional_quantile` histogram panels require complete `_bucket` series and correct `le` labels. Missing buckets or sparse scrape windows can produce unstable tails.
- Direct `delta` on counters, used for PD reconnects and snapshot action/message panels, can be noisy or negative across restarts. `rate`/`increase` may be safer if the metric is a standard monotonic counter.
- `null as zero` plus hidden empty/zero series can hide scrape failures, removed metrics, or dashboard-variable filters that match no series.
- Several panels combine different semantic units in one graph, for example snapshot state count with pending-delete ranges, or heartbeat rate with pending heartbeat gauge. Operators need the legend and axis context to avoid comparing unlike values directly.
- The heatmap for lock queue lengths groups only by `le`, not by instance or additional labels, so it gives cluster-level distribution shape but cannot directly identify the responsible TiKV instance.
- `PD forward status` uses legend `{{instance}}-{{host}}`, but the visible expression groups no labels and directly returns the raw series. If `host` is absent or labels differ across TiKV versions, legends may be confusing.

## Test Signals

Validation should focus on dashboard and PromQL correctness:

- Parse the full `tikv_details.json` as JSON after edits; this chunk alone is not a standalone JSON document because it starts and ends at arbitrary line boundaries.
- Import or provision the dashboard in Grafana to catch duplicate panel IDs, invalid legacy fields, broken collapsed-row nesting, bad heatmap configuration, and datasource variable issues.
- Substitute representative dashboard variable values and validate PromQL expressions with Prometheus query APIs, especially expressions containing `$additional_groupby`, `$optional_quantile`, `histogram_quantile`, and direct `delta`.
- Check TiKV `/metrics` or registry definitions for every referenced metric, including histogram sibling series (`_bucket`, `_sum`, `_count`) used for percentile and average panels.
- Exercise variable combinations with no additional grouping, grouping by `instance`, grouping by subsystem labels such as `type`/`status`, and an `$instance` regex matching one TiKV node and multiple TiKV nodes.
- Visual smoke-test the lock wait queue heatmap, auto-compaction histograms, snapshot percentiles, and resolved-ts gap panels on a live cluster to confirm units, legends, hidden series, and `null as zero` behavior are operationally clear.

## Cross-Chunk Notes

This is chunk 9 for `sources/storage-engines/tikv/metrics/grafana/tikv_details.json` in the chunk manifest. The final per-file research should merge it with adjacent chunks to recover the complete GC row before line 60536, the full panel 486 and remaining `Resolved TS` row after line 68613, and the dashboard-level templating/datasource definitions elsewhere in the JSON.

### subset-b-008915: lines 68614-76906

# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 68614-76906

## Scope

This chunk is a middle slice of TiKV's `tikv_details.json` Grafana dashboard. It starts inside the collapsed `Resolved TS` row, includes the complete collapsed `Point In Time Restore` and `Backup & Import` rows, and ends inside the next collapsed row after the `Total Flushed Size (Last 30m)` log-backup stat panel begins. The file is JSON dashboard configuration rather than executable code, so the important "APIs" are Grafana panel schema fields and Prometheus query expressions that bind TiKV metrics to dashboard views.

## Purpose

- Define operational dashboard panels for TiKV resolved-ts health, PITR/import/backup workloads, external storage setup, checksum/analyze coprocessor work, disk IO, cloud requests, and the first log-backup status/flush panels.
- Provide Prometheus expressions scoped by Grafana variables: `${DS_TEST-CLUSTER}`, `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$__rate_interval`, `$optional_quantile`, and `$additional_groupby`.
- Use collapsed row panels to group related troubleshooting surfaces without making all charts visible by default.
- Standardize graph, heatmap, and stat panels with repeated legend behavior, `null as zero` graph handling, heatmap buckets, and units such as seconds, bytes, bytes/sec, operations/sec, counts/sec, and percent units.

## Important Panels And Query Interfaces

- `Resolved TS` tail panels:
  - `Max gap of resolved-ts in region leaders` uses `tikv_resolved_ts_min_leader_resolved_ts_gap_millis` grouped by `instance`.
  - `Min Leader Resolved TS Region` exposes `tikv_resolved_ts_min_leader_resolved_ts_region`.
  - `Check leader duration` heatmaps `tikv_resolved_ts_check_leader_duration_seconds_bucket`.
  - `CheckLeader request region count` and `CheckLeader request size` calculate `histogram_quantile($optional_quantile, ...)` over check-leader item-count and request-size buckets.
  - `Fail advance ts count` combines `tikv_resolved_ts_fail_advance_count` by `instance, reason` with `tikv_raftstore_check_stale_peer`.
  - `Lock heap size`, `Observe region status`, and `Pending command size` use `tikv_resolved_ts_lock_heap_bytes`, `tikv_resolved_ts_region_resolve_status`, and `tikv_resolved_ts_channel_pending_cmd_bytes_total`.
- `Point In Time Restore` row panels:
  - Import CPU/thread pressure is shown via `tikv_thread_cpu_seconds_total{name=~"sst_.*"}` and `count(rate(...))`.
  - Import RPC latency/ops/count panels use `tikv_import_rpc_duration_bucket`, `_sum`, `_count`, and `tikv_import_rpc_count`, split by request and optional grouping.
  - Apply and engine stages use `tikv_import_apply_duration_bucket`, `tikv_import_engine_request_bucket`, `tikv_import_applier_event`, `tikv_import_apply_bytes_*`, and `tikv_import_apply_cached_bytes`.
  - Memory visibility includes `tikv_server_mem_trace_sum{name=~"raftstore-.*"}`.
- `Backup & Import` row panels:
  - Backup CPU and thread panels use backup worker thread names, `backup_io`, `tikv_backup_softlimit`, and `tikv_backup_thread_pool_size`.
  - Backup error and SST generation panels use `tikv_backup_error_counter`, `tikv_backup_range_size_bytes_bucket`, and `tikv_backup_range_size_bytes_sum`.
  - Backup duration heatmaps and quantile charts use `tikv_backup_range_duration_seconds_bucket`, `_sum`, and `_count` for `snapshot`, `scan`, `save.*`, and all types.
  - External storage creation is represented as both heatmap and percentile/average/count graph over `tikv_external_storage_create_seconds_*`.
  - Checksum/analyze request duration uses `tikv_coprocessor_request_duration_seconds_*{req=~"analyze.*|checksum.*"}`.
  - Disk IO, import CPU/thread/error/RPC/download/read/rewrite/ingest/local-write, raw TTL expiration, and cloud request rate are represented with `node_disk_io_time_seconds_total`, `tikv_import_*`, `tikv_backup_raw_expired_count`, and `tikv_cloud_request_duration_seconds_count`.
- The next row begins with stat panels:
  - `Endpoint Status` maps `tikv_log_backup_enabled` values `0/1` to disabled/enabled text.
  - `Task Status` maps `tikv_log_backup_task_status` values `0/1/2` to running/paused/error text.
  - `Advancer Owner` checks `tidb_log_backup_advancer_owner > 0`.
  - `Average Flush Size`, `Flushed Files (Last 30m) Per Host`, `Flush Times (Last 30m)`, and the beginning of `Total Flushed Size (Last 30m)` use 30-minute `increase` or `delta` windows over `tikv_log_backup_flush_*` metrics.

## Control Flow

Grafana loads this JSON as a dashboard model. Each collapsed row owns a nested `panels` array; when the row is expanded, Grafana evaluates each target expression against the configured Prometheus datasource. Variable interpolation happens before query execution, so cluster and instance filters are injected into every metric selector.

The runtime query pattern is consistent:

- Raw gauges use `sum(...)`, `avg(...)`, or `min(...)` with label grouping.
- Counters use `rate(...)`, `increase(...)`, or `delta(...)` over `$__rate_interval` or fixed `[30m]` windows.
- Histogram charts use either heatmap expressions such as `sum(increase(metric_bucket[$__rate_interval])) by (le)` or quantile expressions using `histogram_quantile(...)` over `sum(rate(metric_bucket[$__rate_interval])) by (..., le)`.
- Stat panels reduce series with `lastNotNull`, while graph panels show time-series legends with current/max values and heatmaps use upper bucket bounds.

## State And Persistence Behavior

This chunk does not persist application data. It persists dashboard configuration: panel IDs, titles, descriptions, row grouping, visual types, units, legends, field mappings, and PromQL expressions. Operational state comes from Prometheus samples emitted by TiKV, TiDB log-backup advancer metrics, and node exporter disk metrics.

The queries themselves imply state semantics:

- Gauge-style metrics such as resolved-ts gap, lock heap bytes, pending command bytes, cached import bytes, backup thread pool size, log-backup enabled/task status, and advancer ownership report current sampled state.
- Counter and histogram metrics are transformed into rates, deltas, increases, quantiles, and heatmap buckets, so restarts and counter resets can affect short-window panels.
- The log-backup stat panels intentionally use fixed `[30m]` windows, while most other panels use Grafana's `$__rate_interval`.
- Several descriptions warn that cumulative flushed sizes or counts may decrease when TiKV nodes reboot; the panel expressions use `delta` over 30 minutes to make recent activity visible despite that reset risk.

## Dependencies And Integration Points

- Grafana dashboard schema: `row`, `graph`, `heatmap`, and `stat` panel types; `fieldConfig`, `options`, `legend`, `tooltip`, `gridPos`, and axis/unit fields.
- Prometheus datasource `${DS_TEST-CLUSTER}` and Grafana variables `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$optional_quantile`, `$additional_groupby`, and `$__rate_interval`.
- TiKV metrics families for resolved-ts, import/PITR, backup, external storage, raw backup TTL, cloud requests, log backup flushes, and server memory tracing.
- TiDB metric `tidb_log_backup_advancer_owner` for advancer ownership, integrated into a TiKV dashboard row.
- Node exporter `node_disk_io_time_seconds_total` for IO utilization correlation during backup/import workloads.
- Visual consumers include on-call debugging, performance analysis, backup/import throughput tracking, and regression detection during TiKV, BR, PITR, or log-backup operations.

## Risks And Edge Cases

- The chunk starts and ends mid-row. Any chunk-local parser must preserve context from neighboring chunks; final dashboard interpretation requires merge/reconciliation with adjacent line ranges.
- Some expressions compare or combine different semantic units in one panel. For example `CheckLeader request size` overlays bytes and item count, and backup CPU overlays CPU utilization with `tikv_backup_softlimit`; legends are required to avoid misreading axes.
- `delta(...)` on counters or reset-prone cumulative values can go negative around process restarts. Some stat panels also use boolean comparisons such as `> 0`, so they show activity presence rather than exact counts.
- Histogram quantiles depend on complete bucket series and correct `le` grouping. Dropped buckets or inconsistent labels will produce misleading quantiles or blank heatmaps.
- Several panels group by `$additional_groupby`. If that variable is empty, malformed, or too high-cardinality, the dashboard can either fail queries or generate excessive series.
- `null as zero` can hide scrape gaps by rendering missing data as zero, especially risky for error counters and status panels.
- The PromQL selectors consistently filter `k8s_cluster`, `tidb_cluster`, and `instance`, but `tidb_log_backup_advancer_owner > 0` does not include those filters in this chunk; depending on datasource scope, it may show advancer owners outside the selected TiKV instance filter.
- The `Import Ingest SST Bytes` heatmap uses `tikv_import_ingest_byte_bucket` but formats the Y axis as seconds in this chunk, which appears inconsistent with the title and metric name.
- The external storage and checksum panels hard-code high percentiles (`0.9999`, `0.99`) alongside average/count series. Sparse workloads can make those percentile lines noisy.
- Stat value mappings use fixed numeric meanings for log-backup enabled/task status. Producer-side enum changes would silently mislabel state unless the dashboard is updated.

## Test Signals

- JSON/dashboard validation should confirm this line range remains syntactically valid when merged with adjacent chunks and that panel IDs `486` through `554` stay unique in the full dashboard.
- PromQL validation should parse every `expr` and `query` field, including expressions with `$optional_quantile` and `$additional_groupby` after variable substitution.
- Dashboard smoke tests should expand `Resolved TS`, `Point In Time Restore`, `Backup & Import`, and the following log-backup row to verify all graph, heatmap, and stat panels render against a representative Prometheus datasource.
- Metric coverage tests should check that TiKV still exports every referenced metric family: `tikv_resolved_ts_*`, `tikv_check_leader_*`, `tikv_import_*`, `tikv_backup_*`, `tikv_external_storage_create_seconds_*`, `tikv_coprocessor_request_duration_seconds_*`, `tikv_cloud_request_duration_seconds_count`, and `tikv_log_backup_*`.
- Unit/axis review should specifically verify `tikv_import_ingest_byte_bucket` formatting and mixed-unit panels.
- Restart/reset scenarios should be tested for panels using `delta` and `increase`, especially backup/log-backup flush counts and sizes.
- Variable tests should exercise empty and non-empty `$additional_groupby`, multiple `$instance` matches, and common `$optional_quantile` values.

### subset-b-008916: lines 76907-85424

# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 76907-85424

## Purpose

This chunk defines a late section of the TiKV details Grafana dashboard. It is declarative dashboard JSON rather than executable code: the operational behavior comes from Grafana rendering panels and Prometheus evaluating the embedded PromQL. The covered lines finish most of the `Backup Log` observability row, then define collapsed rows for `Threads`, `Memory`, `Resource Control`, `Status Server`, `Encryption`, and the beginning of `TTL`.

The main purpose is production troubleshooting for TiKV log backup, advancer progress, process/thread health, allocator behavior, resource control/analyze work, HTTP status server latency, encryption health, and TTL expiration throughput. Every query is scoped through dashboard template variables such as `${DS_TEST-CLUSTER}`, `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$__rate_interval`, `$optional_quantile`, and `$additional_groupby`.

## Important Dashboard Objects and Metrics

The chunk continues the log backup panels with stat, graph, and heatmap objects. Key panels include:

- `Total Flushed Size (Last 30m)` and `Flush Files (Last 30m)`, both using `delta(...[30m])` on `tikv_log_backup_flush_file_size_sum` and `_count`.
- `CPU Usage`, based on `tikv_thread_cpu_seconds_total` for thread names matching `backup_stream|log-backup-scan(-[0-9]+)?`.
- Log backup throughput and progress: `tikv_log_backup_handle_kv_batch_sum`, `tikv_log_backup_incremental_scan_bytes_sum`, `tidb_log_backup_last_checkpoint`, `tikv_log_backup_heap_memory`, and `tikv_log_backup_observed_region`.
- Error panels over `tikv_log_backup_errors` and `tikv_log_backup_fatal_errors`, grouped by `type` and `instance`.
- Duration heatmaps over histogram buckets for flush, initial scan, raft event conversion, region TS resolve, command batch size, temp-file save/write/syscall-write, and advancer tick/batch operations.
- Internal actor panels over `tikv_log_backup_internal_actor_acting_duration_sec_count` and `_bucket`, grouped by message.
- Initial scan RocksDB operation panels using `tikv_log_backup_initial_scan_operations`, trigger reasons via `tikv_log_backup_initial_scan_reason`, pending stages via `tikv_log_backup_pending_initial_scan`, and temp-file cache/swap metrics.
- Advancer checkpoint panels using `tidb_log_backup_advancer_*`, `tidb_log_backup_region_request*`, `tidb_log_backup_current_last_region_id`, `tikv_log_backup_store_last_checkpoint_*`, and `tikv_log_backup_active_subscription_number`.

The collapsed `Threads` row contributes panels for `tikv_threads_state`, `tikv_threads_io_bytes_total`, `tikv_thread_voluntary_context_switches`, and `tikv_thread_nonvoluntary_context_switches`. The `Memory` row covers allocator state through `tikv_allocator_stats`, `tikv_allocator_thread_allocation`, `tikv_allocator_thread_stats`, and `tikv_allocator_arena_count`.

The `Resource Control` row mixes resource-control and analyze metrics: `tikv_resource_control_background_task_wait_duration`, `tikv_resource_control_priority_quota_limit`, `tikv_analyze_metrics_total`, and `tikv_coprocessor_rocksdb_perf` for analyze full sampling block reads. The `Status Server` row uses `tikv_status_server_request_duration_seconds_{bucket,sum,count}` to expose p99/p99.99, average, and operation-rate views by path. The `Encryption` row uses `tikv_encryption_data_key_storage_total`, `tikv_encryption_file_num`, `tikv_encryption_is_initialized`, `tikv_encryption_meta_file_size_bytes`, `tikv_coprocessor_rocksdb_perf` encryption/decryption nanos, and `tikv_encryption_write_read_file_duration_seconds_{bucket,sum,count}`. The chunk ends inside the first `TTL` panel, `tikv_ttl_expire_kv_count_total`; the panel is incomplete in this chunk and should be reconciled with the next chunk.

## Control Flow and Data Flow

Runtime control is Grafana-driven. The JSON creates row panels, most of them collapsed, with nested panels inside each row. When a user expands a row or views the dashboard, Grafana sends each `targets[*].expr` query to the selected Prometheus datasource and renders results according to the panel type.

PromQL data flow follows a few repeated patterns:

- Counter rates use `rate(metric[$__rate_interval])`, usually summed by `instance`, `type`, `reason`, `result`, `stage`, `path`, `message`, or `$additional_groupby`.
- Recent totals use `delta(metric[30m])` for stat panels that show last-30-minute flush size/count.
- Histogram heatmaps use `sum(increase(metric_bucket[$__rate_interval])) by (le)`.
- Quantile graphs use `histogram_quantile(...)` over `sum(rate(..._bucket[$__rate_interval])) by (..., le)`.
- Average latency series divide `sum(rate(..._sum))` by `sum(rate(..._count))`.
- Diagnostic top lists use `topk(20, ...)` with threshold filters for thread IO and context switches.

The dashboard has no local branching logic beyond Grafana options such as `hide`, collapsed rows, legends, axis units, graph overrides, and null handling.

## State and Persistence Behavior

Persistent state is the JSON dashboard definition itself. Operational state comes from Prometheus time series emitted by TiKV and TiDB log backup components. The dashboard reads but does not mutate TiKV state.

The visible state categories in this chunk are:

- Log backup persisted/progress state: checkpoint timestamps, current last region IDs, per-store checkpoint TS/region IDs, active subscriptions, observed region counts, pending initial scan stages, temp-file memory/count/swap size, and flushed files/bytes.
- Process state: thread states, IO bytes, voluntary/nonvoluntary context switches, allocator totals, per-thread allocations, mapped memory, and arena counts.
- Service state: status server request latency/rate by API path.
- Encryption state: key count, encrypted file count, initialization flag, meta file size, crypto nanos, and encryption metadata read/write duration.

Several metrics are counters or histograms that require monotonic series. The stat descriptions note that flush totals may drop after TiKV reboot, because the underlying per-process counters reset.

## Dependencies and Integration Points

This chunk depends on:

- Grafana dashboard JSON schema for row, graph, heatmap, and stat panels.
- The `${DS_TEST-CLUSTER}` datasource variable resolving to Prometheus or a Prometheus-compatible backend.
- Dashboard template variables `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$__rate_interval`, `$optional_quantile`, and `$additional_groupby`.
- TiKV metrics exporters for `tikv_*` series, plus TiDB/log-backup advancer metrics for `tidb_log_backup_*` series.
- Prometheus label contracts including `instance`, `k8s_cluster`, `tidb_cluster`, `name`, `type`, `stage`, `message`, `cf`, `op`, `reason`, `result`, `task`, `priority`, `metric`, `req`, `path`, and `le`.

The integration point with TiKV/TiDB code is metric naming and label stability. Any source-code change that renames log backup, allocator, status server, encryption, analyze, or TTL metrics must update this dashboard. Any change to thread naming also affects the log-backup CPU panel because it filters by thread-name regex.

## Risks and Observability Gaps

- Some panels use `delta` over counters that may reset on restart. The dashboard notes this for flush summaries, but the visual result can still mislead during incident triage.
- `Current Last Region Leader Store ID` appears to query `tikv_log_backup_store_last_checkpoint_ts / 262144`, which looks like a timestamp conversion despite the title saying leader store ID. This may be a dashboard bug or a misleading title.
- `Observed Region Count` repeats the same expression twice, once as `{{instance}}` and once as `{{instance}}-total`, so it may duplicate identical series rather than showing separate per-instance and total views.
- The `Status API Request Duration` panel hides p99.99, average, and count series, leaving p99 visible by default. That is intentional-looking but can hide important tail and traffic context unless users inspect panel settings.
- Several heatmaps aggregate only by `le`, losing `instance` and other labels. This is useful for fleet-level shape but can mask a single slow store.
- The `reason!="retryable-scan-region"` filter in the region checkpoint failure panel suppresses a known retryable category; this reduces noise but can hide a surge in retries.
- Many graph panels use `null as zero`, which can make missing metrics look like true zero values.
- The chunk boundary cuts the TTL row after the query target for `tikv_ttl_expire_kv_count_total`; title, axes, and any subsequent TTL panels are outside this chunk.

## Test and Validation Signals

Useful validation for this chunk is mostly dashboard and metric-contract oriented:

- Load the JSON into Grafana or run a dashboard linter to verify valid panel nesting, unique IDs in the covered range, valid row collapse structure, and supported legacy panel fields.
- Run Prometheus query validation for representative expressions, especially histogram queries, `$additional_groupby` interpolation, and the thread `topk` expressions.
- Verify Prometheus exposes all referenced metrics in a TiKV/TiDB cluster with log backup, encryption, resource control, analyze, and TTL enabled.
- During dashboard review, check that the suspicious leader-store panel and duplicated observed-region expressions match operator intent.
- Exercise restart scenarios to confirm flush stat descriptions and counter-reset behavior are acceptable.
- Compare units against metric semantics: bytes/binBps for size and throughput, seconds for duration, microseconds for resource control quota/wait panels, percentunit for CPU, ops for rates, and none for IDs/counts.

## Cross-Chunk Notes

This is a partial file chunk. It starts mid-panel just before the `Total Flushed Size (Last 30m)` stat title and ends mid-panel in the `TTL` row. The later merge lane should combine this report with adjacent chunks to recover the full `Backup Log` row start and the rest of the TTL dashboard section.

### subset-b-008917: lines 85425-86952

# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 85425-86952

## Chunk Scope

This chunk is the end of the `Test-Cluster-TiKV-Details` Grafana dashboard JSON. It starts inside the `TTL expire count` graph panel, then defines the remaining TTL panels, a collapsed `Config` row, dashboard templating variables, default time range, refresh intervals, and final dashboard identity metadata.

The researched source span is `sources/storage-engines/tikv/metrics/grafana/tikv_details.json:85425-86952`. Because this is a generated/configuration dashboard document rather than executable code, the important "APIs" are Grafana dashboard schema objects, Prometheus query expressions, variable definitions, and panel transformations.

## Purpose

The chunk adds observability for TiKV TTL activity and exposes live TiKV runtime configuration tables. The TTL panels track expiry throughput, checker coverage, checker action rates, compact-task latency, and poll interval. The Config row gives operators instant table views over exported TiKV configuration metrics for RocksDB DB options, RocksDB CF options, flow control, and raftstore options.

The bottom of the file defines the cross-dashboard filter model used by the entire dashboard: Kubernetes cluster, TiDB cluster, database, storage command, instance, Titan database, extra grouping mode, and optional quantile. These variables are substituted into PromQL selectors throughout the dashboard, including the TTL and Config panels in this chunk.

## Important Dashboard Objects and Query Interfaces

### TTL graph/stat panels

- `TTL expire count` is already in progress when the chunk begins. The visible tail shows it is a graph panel with a time x-axis and `none` unit on the primary y-axis. The preceding query context immediately before the chunk uses `tikv_ttl_expire_kv_count_total` as a per-instance rate.
- `TTL expire size` (`id: 624`) is a graph panel at `gridPos x=12,y=0,w=12,h=7`. Its target computes `sum(rate(tikv_ttl_expire_kv_size_total{...}[$__rate_interval])) by (instance)` and displays bytes per second grouped by TiKV instance.
- `TTL check progress` (`id: 625`) computes `sum(rate(tikv_ttl_checker_processed_regions{...}[$__rate_interval])) by (instance) / sum(rate(tikv_raftstore_region_count{type="region",...}[$__rate_interval])) by (instance)`. It is formatted as `percentunit`, implying a progress ratio rather than a raw count.
- `TTL checker actions` (`id: 626`) graphs `sum(rate(tikv_ttl_checker_actions{...}[$__rate_interval])) by (type, $additional_groupby)` with legend `{{type}} {{$additional_groupby}}`. It exposes action throughput by action type and optionally by instance.
- `TTL checker compact duration` (`id: 627`) is a latency/count graph for `tikv_ttl_checker_compact_duration_*`. It renders `histogram_quantile(0.9999, ...)`, `histogram_quantile(0.99, ...)`, average duration from `_sum / _count`, and operation count from `_count`. Series overrides put `count` on y-axis 2 with negative-Y transform and draw `avg` on y-axis 1.
- `TTL checker poll interval` (`id: 628`) is a stat panel using `max(tikv_ttl_checker_poll_interval{type="tikv_gc_run_interval",...})`. It reduces with `lastNotNull`, uses unit `ms`, and shows a current scalar rather than a time-series graph.

All TTL panels use datasource `${DS_TEST-CLUSTER}`, cluster filters `{k8s_cluster="$k8s_cluster", tidb_cluster="$tidb_cluster", instance=~"$instance"}`, and either `$__rate_interval` for rates/histograms or an instant-ish current query for the stat panel.

### Config row and table panels

The collapsed `Config` row (`id: 629`, `type: row`, `collapsed: true`) contains four table panels:

- `RocksDB DB Config` (`id: 630`) queries `tikv_config_rocksdb_db{...}` as an instant table.
- `RocksDB CF Config` (`id: 631`) queries `tikv_config_rocksdb_cf{...} or (tikv_config_rocksdb unless tikv_config_rocksdb_cf)`. The fallback preserves compatibility with exporters that still publish the older `tikv_config_rocksdb` metric instead of the CF-specific metric.
- `Flow Control Config` (`id: 632`) queries `tikv_config_flow_control{...}` as an instant table.
- `Raftstore Config` (`id: 633`) queries `tikv_config_raftstore{...}` as an instant table.

Each table panel uses the same `organize` transformation: hide `Time`, `__name__`, and `job`; rename `name` to `Option`; and rename `Value #A` to `Value`. Field overrides also display the field column as `Option` and the last non-null value as `Value`.

### Dashboard variables and metadata

The chunk closes the panel list and defines the dashboard-wide templating list:

- `k8s_cluster`: hidden query variable from `label_values(tikv_engine_block_cache_size_bytes, k8s_cluster)`.
- `tidb_cluster`: hidden query variable from `label_values(tikv_engine_block_cache_size_bytes{k8s_cluster ="$k8s_cluster"}, tidb_cluster)`.
- `db`: visible multi-select with all enabled, sourced from `label_values(tikv_engine_block_cache_size_bytes{...}, db)`.
- `command`: visible multi-select with all enabled, sourced from non-zero `tikv_storage_command_total` series and regex-extracting the `type` label.
- `instance`: visible multi-select with `allValue: ".*"`, sourced from `label_values(tikv_engine_size_bytes{...}, instance)`. TTL and Config queries rely on this being regex-compatible because selectors use `instance=~"$instance"`.
- `titan_db`: hidden multi-select with all enabled, sourced from `label_values(tikv_engine_titandb_num_live_blob_file{...}, db)`.
- `additional_groupby`: custom variable with `none` and `instance`. TTL action and compact-duration panels include it in `by (...)` clauses and legend text.
- `optional_quantile`: custom variable with `0.99`, `0.999`, `0.9999`, `0.99999`, and `1`. This variable is not consumed by the panels visible in this chunk, but other dashboard chunks may use it for parameterized quantile queries.

Dashboard-level metadata sets `refresh: "1m"`, default time range `now-1h` to `now`, browser timezone, dark style, schema version 14, UID `RDVQiEzZz`, title `Test-Cluster-TiKV-Details`, and version `0`.

## Control Flow and Data Flow

There is no imperative control flow in this JSON. Runtime behavior is driven by Grafana:

1. Grafana loads the dashboard and resolves `${DS_TEST-CLUSTER}` to a Prometheus-compatible datasource.
2. Hidden variables `k8s_cluster` and `tidb_cluster` are populated first from block-cache metrics.
3. Visible variables such as `db`, `command`, and `instance` are populated from label queries constrained by the selected cluster variables.
4. TTL graph panels substitute variables into PromQL selectors and evaluate rates over `$__rate_interval`.
5. Grafana renders time-series panels with shared tooltips, table legends, max/current display, hidden empty/zero series, and nulls rendered as zero for the TTL graphs.
6. The Config row remains collapsed until an operator expands it. Its table panels run instant queries and then apply field transformations to show option/value rows.

The query data path is Prometheus metric export from TiKV to Grafana. The dashboard itself persists only panel definitions, variable definitions, layout, and rendering configuration.

## State and Persistence Behavior

The persisted state is this dashboard JSON, including panel IDs, layout coordinates, variable defaults, refresh policy, and timepicker options. Runtime selections for variables are not meaningfully initialized in this chunk: most `current` entries have `text` and `value` set to `null`, and the custom variables have empty `current` objects. Grafana will resolve these on load or during import.

The `Config` row is persisted with `collapsed: true`, so its four table panels are embedded under the row's `panels` array instead of the top-level visible layout. This matters for dashboard editing and import/export because collapsed-row child panels carry their own `gridPos` relative to the row.

Panel-level state is intentionally minimal. Alerts are not defined; `thresholds` are empty; `links` and `dataLinks` are empty. The dashboard is therefore a read-only observability surface, not an alerting or action surface.

## Dependencies and Integration Points

This chunk depends on these external contracts:

- Grafana dashboard JSON schema version 14 and legacy panel types `graph`, `table`, and `stat`.
- The Prometheus datasource variable `${DS_TEST-CLUSTER}`.
- TiKV metric names: `tikv_ttl_expire_kv_size_total`, `tikv_ttl_checker_processed_regions`, `tikv_raftstore_region_count`, `tikv_ttl_checker_actions`, `tikv_ttl_checker_compact_duration_bucket`, `_sum`, `_count`, `tikv_ttl_checker_poll_interval`, `tikv_config_rocksdb_db`, `tikv_config_rocksdb_cf`, `tikv_config_rocksdb`, `tikv_config_flow_control`, `tikv_config_raftstore`, `tikv_engine_block_cache_size_bytes`, `tikv_storage_command_total`, `tikv_engine_size_bytes`, and `tikv_engine_titandb_num_live_blob_file`.
- Required labels include `k8s_cluster`, `tidb_cluster`, `instance`, `type`, `db`, `name`, and histogram bucket label `le`.
- Grafana variable substitution semantics for `$__rate_interval`, `$k8s_cluster`, `$tidb_cluster`, `$instance`, and `$additional_groupby`.

Integration-wise, the TTL panels tie TiKV's TTL subsystem to raftstore region count and compaction-duration histograms. The Config row integrates TiKV's exported configuration metrics with Grafana table transformations so operational configuration can be inspected without shelling into TiKV nodes.

## Risks and Edge Cases

- `TTL check progress` divides a rate of processed regions by a rate of region count. Region count is typically a gauge-like count; using `rate()` on it can produce zero, negative, or noisy denominators when region count changes slowly. That can make the progress ratio unstable or empty.
- `$additional_groupby` includes `none`, and this chunk interpolates it directly into `by (type, $additional_groupby)` and `by ($additional_groupby)`. PromQL support for a literal `none` label only works as a grouping label with no matching label values; it does not mean "group by nothing". This may create confusing empty legend segments or unintended grouping unless upstream dashboard generation intentionally uses a synthetic `none` label pattern.
- Several graph panels use `nullPointMode: "null as zero"`. Missing exporter data, scrape failures, or label mismatch can look like real zero throughput.
- Config panels use instant table queries with `maxDataPoints: 100`. Clusters with many options, instances, or label combinations may truncate or crowd table output.
- The RocksDB CF config fallback `tikv_config_rocksdb unless tikv_config_rocksdb_cf` is useful for compatibility but can mix legacy and current metric shapes if both are partially present.
- Template variables are bootstrapped from block-cache and engine-size metrics. If those metrics are missing while TTL or config metrics exist, variables may fail to populate and downstream panels will appear empty.
- Grafana schema version 14 and old `graph`/`table` panel settings may need migration in newer Grafana versions; field config and transformation fields are a mix of old and newer panel APIs.

## Test and Validation Signals

Useful validation for this chunk should include:

- Import `tikv_details.json` into a supported Grafana version and verify the dashboard parses with UID `RDVQiEzZz` and title `Test-Cluster-TiKV-Details`.
- In a Prometheus test environment with TiKV metrics, check that all variable queries populate in this order: `k8s_cluster`, `tidb_cluster`, `instance`, `db`, `command`, and `titan_db`.
- Run the TTL PromQL expressions directly in Prometheus for selected clusters and verify no parse errors occur, especially queries using `$additional_groupby`.
- Compare `TTL expire count` and `TTL expire size` with known TTL expiry workloads to confirm the counters are monotonic and the byte panel uses the expected `bytes` unit.
- Validate `TTL checker compact duration` by checking that `_bucket`, `_sum`, and `_count` series share compatible labels and that histogram quantiles produce non-empty series.
- Expand the collapsed Config row and verify each table shows `Option` and `Value` columns after the `organize` transformation, with `Time`, `__name__`, and `job` hidden.
- Exercise the `instance=All` path and confirm `allValue: ".*"` produces valid regex selection in every TTL and Config query in this chunk.

## Chunk Handoff Notes

For final per-file reconciliation, this chunk should be merged with earlier `tikv_details.json` chunks as the dashboard footer. Its main cross-chunk dependencies are the start of the `TTL expire count` panel before line 85425 and any earlier panels that consume `optional_quantile`, `db`, `command`, or `titan_db`. This chunk supplies the final dashboard-level variable definitions and therefore helps explain variable references appearing throughout the full file.
