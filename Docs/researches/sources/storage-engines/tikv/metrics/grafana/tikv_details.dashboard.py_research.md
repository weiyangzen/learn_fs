# Research: sources/storage-engines/tikv/metrics/grafana/tikv_details.dashboard.py

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008904`: lines 1-6725, `Docs/researches/chunks/subset-b-008904_research.md`
- `subset-b-008905`: lines 6726-11011, `Docs/researches/chunks/subset-b-008905_research.md`

## Chunk Research

### subset-b-008904: lines 1-6725

# sources/storage-engines/tikv/metrics/grafana/tikv_details.dashboard.py lines 1-6725

## Chunk Scope

This chunk covers the imports, dashboard template variables, and the first large run of row-builder functions in `tikv_details.dashboard.py`. It starts with the `common.py`/`grafanalib` dependency setup, defines `Templates()`, and then defines dashboard rows from `Duration()` through most of `RocksDB()`.

The line boundary cuts inside `RocksDB()`: lines through 6722 finish the block-cache-operations row, and line 6725 is the opening `graph_panel(` for the following `Read flow` row. The rest of `RocksDB()` and all later TiKV detail rows belong to later chunks.

## Purpose

This file is a Python generator for the TiKV Details Grafana dashboard. The functions in this chunk return `grafanalib.core.RowPanel` objects populated with Prometheus targets for TiKV health, latency, throughput, scheduler, Raft, GC, coprocessor, in-memory engine, thread, and RocksDB diagnostics.

The code is mostly declarative: each row function constructs a `Layout`, adds rows of `graph_panel`, `heatmap_panel`, `stat_panel`, or histogram helper outputs, then returns `layout.row_panel`. The operational contract is the generated dashboard JSON, not runtime TiKV behavior. Correctness depends on accurate Prometheus metric names, label selectors, legends, units, repeat variables, and row ordering.

## Important APIs, Types, and Functions

- `Templates() -> Templating` defines Grafana variables for `k8s_cluster`, `tidb_cluster`, `db`, `command`, `instance`, `titan_db`, `additional_groupby`, and `optional_quantile`. These variables drive every generated query that uses the default selectors or `$db`/`$command` repeats.
- `Layout` from `common.py` owns Grafana row placement. `layout.row([...])` assigns 24-column grid positions and appends panels to the row; `layout.half_row([...])` creates half-width rows used in GC.
- `target()` from `common.py` converts `Expr`, `OpExpr`, or raw PromQL strings into Grafana `Target` objects. If `additional_groupby=True`, it appends `$additional_groupby` to the PromQL `by (...)` clause and legend.
- `expr_sum`, `expr_avg`, `expr_max`, `expr_sum_rate`, `expr_sum_delta`, `expr_sum_aggr_over_time`, `expr_histogram_quantile`, `expr_histogram_avg`, `expr_operator`, and `expr_topk` build PromQL with default cluster filters: `k8s_cluster`, `tidb_cluster`, and `instance=~"$instance"` unless explicitly skipped.
- `graph_panel_histogram_quantiles()` and `heatmap_panel_graph_panel_histogram_quantile_pairs()` provide common histogram views: heatmap buckets plus quantile/count/avg graph panels.
- `YatpPool()` is the only reusable row-builder defined in this chunk. `UnifiedReadPool()` and `SchedulerWorkerPool()` call it with different pool prefixes and running-task metrics.
- `SchedulerCommands()` and `RocksDB()` use Grafana row repeat behavior: `repeat="command"` and `repeat="db"` respectively.

## Row Builders Covered

- `Duration()` summarizes write-pipeline and coprocessor read latency with optional quantiles.
- `Cluster()` gives top-level storage capacity, CPU, memory, disk I/O, QPS/error rate, leader/region counts, buckets, and uptime.
- `Errors()` groups critical errors, busy signals, raftstore/scheduler/coprocessor/gRPC errors, leader drop/missing, damaged files, and append rejects.
- `Server()` covers CF size, channel full, active written leaders, region size/write distributions, hibernated peers, raftstore memory trace, raft entry cache eviction, address resolution, YATP wait latency, and RocksDB perf read I/O.
- `gRPC()` covers message counts, failures, message duration, batch wait and batch size, request sources, and resource-group QPS.
- `ThreadCPU()` groups thread CPU usage by TiKV subsystem and includes top busy non-RocksDB threads.
- `TTL()` covers TTL expiration, checker progress/actions, compact duration, and poll interval.
- `PD()` covers PD requests, request durations, heartbeats, validation, reconnects, forwarding, and pending TSO requests.
- `IOBreakdown()` covers `tikv_io_bytes`, rate limiter thresholds, and wait duration.
- `RaftWaterfall()`, `RaftstoreIO()`, `RaftIO()`, `RaftPropose()`, `RaftProcess()`, `RaftMessage()`, `RaftAdmin()`, `RaftLog()`, and `LocalReader()` cover Raft write-path timing, IO reasons, proposal/read/write rates, FSM scheduling/polling, message transport, split/admin events, log GC/fetch behavior, and local-reader request counters.
- `Storage()`, `FlowControl()`, `SchedulerCommands()`, `Scheduler()`, `SchedulerWorkerPool()`, and `GC()` cover storage async request timing/errors, full compaction, concurrency manager timestamps, write throttling, scheduler command stages, per-command scheduler details, scheduler memory/pending/running state, YATP scheduler pool behavior, TiDB/TiKV GC, safe points, compaction filter GC, and auto compaction candidate metrics.
- `Snapshot()` and `Task()` cover raft snapshot traffic/actions/durations/sizes/pending applies and worker/future-pool task throughput/backlog.
- `CoprocessorOverview()` and `CoprocessorDetail()` cover coprocessor request duration, errors, scan keys, RocksDB perf, response bytes, memory quota, DAG executor/request counts, scan details by CF, memory-lock checks, semaphore waits, and waiting task counts.
- `InMemoryEngine()` covers in-memory engine operations, RocksDB-vs-IME read throughput, cache hit/miss behavior, memory/region counts, GC/load/eviction/warmup, write/prepare/seek durations, safe point range, and auto load/evict histograms.
- `Threads()` covers OS thread state, thread I/O, and voluntary/nonvoluntary context switch top-k panels.
- `RocksDB()` starts a repeated per-`db` row group and, in this chunk, covers get/seek/write/WAL operations, latency summaries, compaction operations/durations/job file counts, SST read duration, compaction reasons, block cache size, memtable hit rate, block cache byte flow, block cache hit rates, key flow, and block cache operation counts. Subsequent RocksDB rows are outside the chunk.

## Control Flow

There is no conditional runtime flow tied to TiKV state. Each builder follows the same static construction pattern:

1. Create a `Layout(title=...)`, sometimes with `repeat=...`.
2. Call `layout.row()` or `layout.half_row()` with a list of panel objects.
3. Each panel embeds one or more `target()` calls.
4. Each target embeds a PromQL expression built from `common.py` helpers or, rarely, a raw string.
5. Return `layout.row_panel` for later assembly into the full `Dashboard`.

The main dynamic behavior is delegated to Grafana and Prometheus. Grafana resolves template variables such as `$db`, `$command`, `$instance`, `$additional_groupby`, and `$optional_quantile`; Prometheus evaluates the generated expressions over `$__rate_interval` or explicit ranges like `1m` and `30s`.

## State and Persistence Behavior

This chunk has no mutable application state, no persistence, no network I/O, and no direct filesystem writes. Its state is the generated Grafana dashboard schema. The durable output is produced later when the script is rendered to JSON, which is expected to align with `tikv_details.json` and its checksum file.

Template variables act as dashboard-level state from a user perspective: changing `db`, `command`, `instance`, `additional_groupby`, or `optional_quantile` changes query shape and panel cardinality. `repeat="db"` and `repeat="command"` create multiple row instances based on variable values.

## Dependencies

- Local `common.py` supplies the DSL for PromQL expression construction, Grafana target creation, panel creation, units, layout, legends, series overrides, and templating.
- `grafanalib.formatunits` supplies display units such as seconds, bytes IEC, bytes/sec IEC, percent, ops/sec, requests/sec, microseconds, nanoseconds, and ISO timestamps.
- `grafanalib.core` supplies dashboard object types and constants, including `Templating`, `RowPanel`, `GraphThreshold`, `StatValueMappings`, `StatValueMappingItem`, `Dashboard`, `NULL_AS_NULL`, and tooltip/hide constants.
- Prometheus metrics are emitted by TiKV, TiDB clients, PD interactions, node exporters, RocksDB/raft-engine instrumentation, and subsystem-specific workers. The dashboard assumes those metric and label contracts exist.

## Integration Points

- The default selectors in `common.Expr` integrate every generated query with TiDB Cloud/TiKV label dimensions: `k8s_cluster`, `tidb_cluster`, and `instance`.
- `Templates()` provides the variable names used by the generated PromQL, including `$db` for `RocksDB()` and `$command` for `SchedulerCommands()`.
- `additional_groupby=True` is an integration mechanism for optional per-instance drilldown without duplicating panels. It appends `none` or `instance` depending on the template variable value.
- Histogram helpers depend on Prometheus histogram naming conventions: callers pass the base metric without `_bucket`, `_sum`, or `_count`; helpers synthesize those suffixes.
- `skip_default_instance_selector()` is used for TiDB-side GC/config metrics and some safe-point panels where the TiKV `instance` selector would be wrong or too restrictive.
- Series overrides are used where panels combine different scales, for example running compactions/flushes on the right axis and pending raft log fetch tasks on a secondary axis.

## Risks and Edge Cases

- Metric rename or label drift breaks panels silently at dashboard runtime. The highest-risk areas are regex label selectors for thread names, `db="$db"`, `type="$command"`, and detailed RocksDB `type` labels such as percentile names.
- `target(additional_groupby=True)` mutates the expression by appending `$additional_groupby`. Reusing the same `Expr` object across targets would duplicate labels, though this chunk generally creates fresh expressions inline.
- `target()` assumes an `Expr` with `additional_groupby=True` has or receives a non-`None` legend. Expressions with empty `by_labels` rely on explicit legends in this file; missing one can fail string concatenation or produce poor legends.
- Several ratio panels divide by sums that can be zero, including cache hit rates, bloom prefix rate, TTL progress, and in-memory engine hit rate. Prometheus will produce `NaN`/`Inf` rather than a guarded zero.
- Optional quantile panels use `$optional_quantile` in both query and legend. Invalid custom variable values would generate invalid PromQL.
- The chunk contains raw strings and manually assembled label selectors; typos are not caught until rendering or dashboard use. One visible example is `by_labels=["cf", " type"]` in the RocksDB compaction guard panel, where `" type"` includes a leading space.
- Line 6725 opens a row whose contents are outside this chunk. Any analysis of `RocksDB()` must be reconciled with following chunks before a final per-file report.

## Test Signals

- Run the dashboard generation path that produces `tikv_details.json` and compare it with the checked-in JSON/checksum to catch layout, query, and schema drift.
- Import or render the generated `Dashboard` with `grafanalib` to catch Python syntax errors, invalid object fields, missing legend formats for `OpExpr`, and invalid unit constants.
- Snapshot-test representative PromQL strings for default selectors, `skip_default_instance_selector()`, `additional_groupby=True`, optional quantiles, repeated `$db`/`$command` rows, and histogram helper suffix generation.
- Validate that every base histogram metric passed to `expr_histogram_quantile()` or `expr_histogram_avg()` omits `_bucket`, `_sum`, and `_count`, matching the helper assertions.
- Lint or query-check label names in `by_labels`, especially the RocksDB `["cf", " type"]` case and high-cardinality additions from `$additional_groupby`.
- Runtime dashboard smoke tests should exercise template combinations: all instances, a single instance, all DBs, one DB, all commands, one command, and `additional_groupby=instance`.
- Prometheus-side tests should verify key panels return data for a sample TiKV deployment: cluster capacity, gRPC duration, scheduler command repeat rows, GC safe points, in-memory engine panels when enabled, and RocksDB repeated rows.

### subset-b-008905: lines 6726-11011

# sources/storage-engines/tikv/metrics/grafana/tikv_details.dashboard.py lines 6726-11011

## Scope

This chunk covers the final large segment of TiKV's generated Grafana details dashboard definition. It starts in the latter part of `RocksDB()` at the "Read flow" panel and continues through the remaining row-panel factory functions plus the final `Dashboard(...)` assembly.

Functions wholly or partially covered here:

- tail of `RocksDB()` from read/write flow panels through write-stall and memtable panels;
- `RaftEngine()`;
- `Titan()`;
- `PessimisticLocking()`;
- `PointInTimeRestore()`;
- `ResolvedTS()`;
- `Memory()`;
- `BackupImport()`;
- `Encryption()`;
- `BackupLog()`;
- `SlowTrendStatistics()`;
- `StatusServer()`;
- `ResourceControl()`;
- `LoadShedding()`;
- `TikvConfig()`;
- the final `dashboard = Dashboard(...).auto_panel_ids()` object.

The code is declarative dashboard construction rather than TiKV runtime logic. Each function creates a `Layout`, appends Grafana rows with panel helper calls, and returns `layout.row_panel`.

## Purpose

- Define the lower half of the `Test-Cluster-TiKV-Details` Grafana dashboard used to observe TiKV engine internals, transaction lock behavior, backup/import tools, log backup, resource control, status API, encryption, and config surfaces.
- Encode Prometheus queries, panel titles, legends, units, row grouping, stat value mappings, and final dashboard ordering in Python/grafanalib form.
- Keep the dashboard close to TiKV metric names so dashboard generation fails or produces visibly broken panels when metric contracts drift.
- Provide specialized views for operational diagnosis: RocksDB read/write/compaction flow and stalls, raft-engine WAL behavior, Titan blob storage, pessimistic-lock wait/deadlock behavior, PITR/import and backup throughput, resolved-ts health, allocator behavior, log backup checkpoint lag, load shedding, and static TiKV configuration gauges.

## Important APIs, Types, And Functions

- `Layout` is the local dashboard-row builder imported from `common`. Every function in this chunk instantiates `Layout(title=...)`, optionally with `repeat="titan_db"` in `Titan()`, then calls `layout.row([...])`.
- `graph_panel`, `graph_panel_histogram_quantiles`, `heatmap_panel`, `stat_panel`, and `table_panel` create Grafana panels. The chunk uses graph panels for time series, heatmaps for Prometheus histogram buckets, stat panels for current log-backup status, and table panels for config metrics.
- `target(...)` wraps Prometheus expressions and per-series metadata such as `legend_format`, `hide`, and `additional_groupby`.
- PromQL expression helpers include `expr_simple`, `expr_sum`, `expr_avg`, `expr_max`, `expr_min`, `expr_sum_rate`, `expr_count_rate`, `expr_sum_delta`, `expr_sum_increase`, `expr_sum_aggr_over_time`, `expr_histogram_quantile`, `expr_operator`, and `expr_topk`. They are the main abstraction that keeps label selectors and aggregate labels consistent across panels.
- `yaxes(...)` and `yaxis(...)` bind Grafana units from `grafanalib.formatunits` such as bytes, bytes/sec, seconds, microseconds, milliseconds, ops/sec, percent, date-time, and short numeric formats.
- `OPTIONAL_QUANTILE_INPUT` is interpolated into several titles and legends for panels whose histogram quantile can be chosen from the dashboard variable defined earlier in the file.
- `StatValueMappings` and `StatValueMappingItem` map log-backup status gauge values to readable states: endpoint disabled/enabled and task running/paused/error.
- `series_override(...)` is used in the log-backup checkpoint panel to render the synthetic current-time series as a dashed reference line.
- `Dashboard(...)` sets dashboard metadata and composition: title `Test-Cluster-TiKV-Details`, UID `RDVQiEzZz`, browser timezone, one-minute refresh, datasource input, `Templates()`, ordered panel list, schema version 14, and shared-crosshair graph tooltip.

## Panel Coverage

The `RocksDB()` tail covers engine read/write and storage health: `tikv_engine_flow_bytes`, `tikv_engine_estimate_num_keys`, `tikv_engine_compaction_flow_bytes`, `tikv_engine_bytes_per_read`, `tikv_engine_bytes_per_write`, `tikv_engine_read_amp_flow_bytes`, `tikv_engine_pending_compaction_bytes`, snapshot count and oldest snapshot duration, compression ratios, files per level, ingest-SST duration and picked level, RocksDB block-read perf counters, write-stall reasons/durations, stall condition changes, and memtable size.

`RaftEngine()` covers raft-engine operations, write/read/message rates, write duration and breakdowns, WAL sync/allocation/rotation duration, write size, rewrite flow, log/swap/recycle file counts, entry count, purge/read durations, and write compression ratio. It uses both fixed 0.999 quantiles and optional 0.99-style quantiles.

`Titan()` repeats per `$titan_db` and covers TitanDB blob-file count/size, blob cache size and hit ratio, iterator-touched blob-file count, blob key/value sizes, blob get/seek/next/prev durations, blob locate operation rates, discardable ratio distribution, blob key/byte flow, blob file read/write/sync durations, blob GC action/duration/input/output sizes, GC key/byte flow, and GC file count.

`PessimisticLocking()` covers lock-manager CPU, handled tasks, waiter lifetime, wait-table status, lock-wait queue entries, deadlock detection duration and errors, detector leader heartbeat, pessimistic lock memory, in-memory pessimistic-lock results, active keys/waiters, wait queue length heatmap, and in-memory scan-lock read duration.

`PointInTimeRestore()` focuses on PITR apply/import paths: SST worker CPU, apply RPC duration, download/apply engine breakdown, apply RPC ops/counts, cache events, RPC and apply heatmaps, queuing/concurrency/apply time, throughput, applier speed, cached bytes, unfinished engine requests, and raftstore memory usage during apply.

`ResolvedTS()` covers resolved-ts/advance-ts/scan-lock worker CPU, gaps between resolved/safe timestamps and wall-clock time, region IDs with minimal resolved/safe timestamps, check-leader duration/request size/item count, failed advancement reasons and stale-peer checks, lock heap bytes, initial scan backoff, observe-region status, and pending command bytes.

`Memory()` covers allocator statistics, net allocation rate per thread (`alloc - dealloc`), allocated/released rates, mapped allocation, and arena count.

`BackupImport()` combines backup, import, checksum, and cloud-request views: backup CPU/thread count/errors, SST size and duration histograms, SST generation throughput, external storage creation, checksum/analyze duration, node disk IO utilization, import CPU/thread/errors, import RPC duration/rates/counts, download/read/rewrite/ingest heatmaps, download throughput, local write keys/bytes, TTL expired count, and cloud request rate.

`Encryption()` covers encryption data keys, encrypted file count, initialization flag, meta file size, coprocessor RocksDB encryption/decryption nanos, and encryption metadata read/write duration.

`BackupLog()` is the largest single section. It covers endpoint/task/owner status, recent flush file/size stats, average flush size, log-backup CPU, handle event rate, initial scan throughput, checkpoint lag, event memory, observed regions, retryable/fatal errors, checkpoint TS versus current time, flush/initial-scan/convert/resolve durations, command batch sizes, temp-file save/write/syscall durations, internal actor message rates/durations, initial scan RocksDB throughput/operations, initial scan reason/status, temp buffer memory/file/swap metrics, advancer batch/tick durations, region checkpoint request failures/results, current last region/checkpoint/store state, active subscriptions, and advancer operation counts.

`SlowTrendStatistics()`, `StatusServer()`, `ResourceControl()`, `LoadShedding()`, and `TikvConfig()` provide smaller operational sections for slow-store detection, status API latency/rate, resource-control/analyze metrics, admission/load-shedding behavior, and table views of TiKV config gauges.

## Control Flow

The runtime flow of the Python script is straightforward:

1. Import grafanalib types, format units, and local `common` helpers.
2. Define row-panel factory functions. The functions are not executed until the final `Dashboard` object is built.
3. Inside each factory, instantiate a `Layout`.
4. Call `layout.row([...])` repeatedly with panel objects. Each panel contains one or more `target()` objects, and each target contains a PromQL string or an expression-builder object.
5. Return `layout.row_panel`.
6. Build `dashboard = Dashboard(...)` at module import/execution time. The `panels=[...]` list calls every row-panel factory in the intended dashboard order, including functions defined before this chunk and functions defined in this chunk.
7. Call `.auto_panel_ids()` to assign Grafana panel IDs after all row panels are assembled.

There are no loops in this chunk except implicit iteration inside helper calls and Grafana rendering. Branching is limited to PromQL expression composition through helpers such as `.extra(" > 0")`, `expr_operator(a, "/", b)`, and stat value mappings.

## State And Persistence Behavior

- The Python code itself stores no TiKV runtime state and writes no TiKV data. Its only stateful local objects are transient `Layout`, panel, target, and `Dashboard` Python objects created while generating the Grafana dashboard JSON.
- Persistence impact is indirect: this file defines the persisted dashboard artifact when the dashboard generator is run. Generated JSON panel IDs, row order, query strings, and template references become part of the operational monitoring surface.
- The panels observe persistent TiKV subsystems such as RocksDB, raft engine, Titan blob files, backup/import files, log backup checkpoints, and configuration gauges, but they do not mutate those systems.
- `Dashboard(...).auto_panel_ids()` makes panel identity generation dependent on the final ordered panel tree. Reordering, adding, or removing row panels changes generated IDs and may affect Grafana links/alerts if any external artifact depends on panel IDs.
- `TikvConfig()` table panels expose config metrics as Prometheus samples. They do not read TiKV config files directly; they depend on TiKV exporting config gauge labels.

## Dependencies And Integration Points

- Depends on `metrics/grafana/common.py` helper functions for PromQL generation, datasource input handling, panel construction, templating, grouping, and axes. The correctness of `additional_groupby=True`, label selectors, histogram helpers, and `.extra(...)` suffix behavior is delegated to this module.
- Depends on `grafanalib.core` for `Dashboard`, `RowPanel`, `Templating`, stat value mappings, tooltip mode, null-point handling, and visibility constants.
- Depends on `grafanalib.formatunits` for all Grafana unit strings. Incorrect units do not break Prometheus queries but make panels misleading.
- Depends on templates defined earlier in this file: `$db`, `$titan_db`, `$instance`, `$additional_groupby`, `$optional_quantile`, `$k8s_cluster`, and `$tidb_cluster`. Many expressions in this chunk interpolate `db="$db"` or `db="$titan_db"` directly.
- Integrates with Prometheus metric names exported by TiKV, TiDB log-backup advancer, and node exporter. Examples include `tikv_engine_*`, `raft_engine_*`, `tikv_lock_manager_*`, `tikv_import_*`, `tikv_resolved_ts_*`, `tikv_log_backup_*`, `tidb_log_backup_*`, `tikv_resource_control_*`, `tikv_status_server_*`, and `node_disk_io_time_seconds_total`.
- Integrates with Grafana dashboard consumers rather than TiKV production code. The final dashboard is usually rendered to JSON by the repository's dashboard tooling and then imported into Grafana.
- The final `panels=[...]` ordering integrates functions from the whole file: earlier overview/raftstore/scheduler/read-pool/GC/task sections plus the chunk-defined engine/tool/debug/infrequent/config sections.

## Risks And Edge Cases

- Metric rename or label drift is the primary risk. The code hard-codes many metric names and labels such as `db`, `type`, `cf`, `level`, `instance`, `request`, `stage`, `resource_group`, and `is_background`; any exporter change can silently produce empty panels.
- Template coupling is tight. `Titan()` requires the hidden `titan_db` variable, and RocksDB panels require `$db`. If template queries stop returning values, repeated rows or db-filtered panels disappear.
- `additional_groupby=True` relies on the `common` helper to merge an optional dashboard grouping label into PromQL. A helper regression can affect many panels at once.
- Some panels intentionally override default instance grouping with `by_labels=[]`. That gives cluster-wide totals/averages but can hide per-instance skew if copied into a diagnosis that needs instance-level detail.
- Several PromQL ratios can divide by zero or produce missing/NaN series: RocksDB read amplification, Titan blob-cache hit ratio, backup average flush size, and checkpoint lag expressions with post-filtered timestamps.
- Heatmap panels require `_bucket` metrics with stable bucket label semantics. Supplying a base histogram metric to `heatmap_panel` or changing buckets in exporters would break visual distributions.
- Histogram quantile panels depend on bucket cardinality and label grouping. Adding high-cardinality labels to metrics can make panels expensive, especially in Titan, backup/import, log backup, and resolved-ts sections.
- The chunk mixes fixed quantiles, optional quantiles, histogram averages, rates, deltas, and increases. Using `delta` on counters over short windows can show resets/reboot artifacts; some log-backup stat descriptions explicitly warn that values may reduce after TiKV reboot.
- There are a few text-quality issues that do not affect functionality but can reduce operator clarity, such as typos in panel titles/descriptions (`durtion`, `Subscrption`, "summered") and duplicate or swapped-looking labels in Titan blob file read/write duration panels where 99/95 selector labels are paired with 95/99 legends.
- `schemaVersion=14` is deliberately kept at or above the Grafana threshold for shared crosshair/tooltips. Lowering it can break the intended tooltip behavior.
- Panel ID stability depends on `auto_panel_ids()` and the ordered panel list. Merge conflicts or out-of-order insertion can produce a dashboard that renders but changes panel IDs unexpectedly.
- Table config panels use raw config gauges. Label cardinality or string-like labels can make tables wide, and the fallback expression for RocksDB CF config (`tikv_config_rocksdb unless tikv_config_rocksdb_cf`) assumes exporter compatibility behavior.

## Test Signals

- The most direct validation is running the repository's Grafana dashboard generation path for `tikv_details.dashboard.py` and confirming it imports without Python exceptions and emits valid Grafana JSON.
- Generated JSON should be checked for non-empty row panels for every function in this chunk, stable panel IDs after `.auto_panel_ids()`, and presence of the expected dashboard UID/title/schema/tooltips.
- Static checks can parse generated targets and verify that every PromQL expression is syntactically valid, especially expressions assembled with `expr_operator(...)`, `.extra(...)`, regex label selectors, and `time() * 1000` checkpoint computations.
- A Prometheus-backed smoke test should load the dashboard against a TiKV test cluster and verify representative panels return data for RocksDB, raft engine, backup/import, resolved-ts, log backup, resource-control, and config metrics.
- Metric-contract tests should spot-check important metric names in TiKV exporters against dashboard references: `tikv_engine_flow_bytes`, `raft_engine_write_duration_seconds`, `tikv_engine_titandb_num_live_blob_file`, `tikv_lock_manager_waiter_lifetime_duration`, `tikv_import_rpc_duration`, `tikv_resolved_ts_min_resolved_ts_gap_millis`, `tikv_log_backup_enabled`, `tidb_log_backup_last_checkpoint`, and `tikv_config_rocksdb_db`.
- Visual review should verify units and legends: bytes versus bytes/sec, seconds versus microseconds, ops/sec versus counts, date-time checkpoint panels, hidden import thread targets, stat value mappings, and dashed current-time series override.
- Regression tests for this chunk should compare generated dashboard JSON before/after changes while allowing intentional panel additions. Unintended changes to row order, repeated row variables, template references, or panel IDs are important review signals.
