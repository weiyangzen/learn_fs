# sources/storage-engines/tikv/metrics/grafana/tikv_raw.json

## Purpose

`tikv_raw.json` is a Grafana dashboard export named `Test-Cluster-TiKV-Raw` with UID `K0D2tEZZz`. It focuses on TiKV raw read commands and causal timestamp provider behavior. The dashboard is intentionally narrower than the fast-tune board: it helps operators inspect latency for raw read command classes and diagnose TSO/causal timestamp request volume, renewal latency, batch-list behavior, and current batch size.

The default time range is the last five minutes and `refresh` is disabled in the export. The dashboard uses Grafana dark style, schema version `16`, and has two collapsed top-level rows: `Read - $command` and `Causal timestamp`. Those collapsed rows contain all graph panels, so a viewer must expand them to see the charts.

## Important APIs, Types, and Functions

This file is dashboard configuration rather than executable code, but its operational interface is the combination of Grafana dashboard schema, template variables, and PromQL:

- Dashboard fields include `__inputs`, `__requires`, `annotations`, `templating`, `panels`, `time`, `timepicker`, `refresh`, `uid`, and `version`.
- The datasource input is `DS_TEST-CLUSTER`, labeled `test-cluster`, with Prometheus plugin metadata.
- Required components are Grafana `5.4.3`, Graph panel `5.0.0`, and Prometheus datasource `5.0.0`.
- Template variables include hidden `k8s_cluster` and `tidb_cluster`, visible multi-select `command`, and visible multi-select `instance`.
- The `command` variable is populated from `tikv_storage_command_total` and regex-filtered to `raw_get|raw_scan|raw_batch_get|raw_batch_scan`.
- The `instance` variable is populated from `tikv_engine_size_bytes` for the selected cluster labels.
- PromQL target expressions use `rate`, `sum`, and `histogram_quantile` over one-minute windows.

The dashboard reads scheduler command and read-processing histograms for raw commands: `tikv_scheduler_command_duration_seconds_bucket`, `_sum`, `_count`, and `tikv_scheduler_processing_read_duration_seconds_bucket`, `_sum`, `_count`. It also reads causal timestamp provider metrics: `tikv_causal_ts_provider_get_ts_duration_seconds_bucket/count`, `tikv_causal_ts_provider_tso_batch_renew_duration_seconds_bucket/count`, `tikv_causal_ts_provider_tso_batch_list_counting_bucket/count`, and `tikv_causal_ts_provider_tso_batch_size`.

## Control Flow

Grafana first resolves the hidden cluster selectors from Prometheus. `k8s_cluster` is discovered from `tikv_engine_block_cache_size_bytes`; `tidb_cluster` is discovered from the same metric family constrained by the selected Kubernetes cluster. The visible `command` selector is then built from `tikv_storage_command_total` and restricted to raw read commands. The visible `instance` selector is built from `tikv_engine_size_bytes` for the chosen cluster.

When the `Read - $command` row is expanded, the dashboard renders `Command Duration` and `Read Processing Duration`. Each panel shows P99, P95, and average latency for the selected raw command regex and selected instances. The P99/P95 series are derived from histogram buckets, while average latency divides one-minute `_sum` rate by one-minute `_count` rate.

When the `Causal timestamp` row is expanded, the dashboard renders causal timestamp request rate by result, P99/P999/MAX get-ts duration by result, TSO batch renew request rate by result and reason, P99 renew duration by result and reason, P99/P50 TSO batch-list counting by type, batch-list counting frequency by type, and current summed TSO batch size.

The source contains two top-level row panels, nine graph panels nested under those rows, and sixteen Prometheus target expressions.

## State and Persistence Behavior

The file persists dashboard structure and identity, not metric data. The export has `uid: "K0D2tEZZz"`, `version: 1`, `iteration: 1560225374091`, `editable: true`, `id: null`, and `gnetId: null`. Both top-level rows have `collapsed: true`, so the nested panels are stored under each row's `panels` field rather than as visible top-level graph panels. Runtime state comes from Grafana variable selections and the active time range.

Because the default time range is only five minutes and every rate uses a one-minute window, the dashboard is optimized for immediate inspection. It is less useful for long-term trend analysis unless the viewer manually expands the range and verifies that the one-minute rates remain appropriate.

## Dependencies and Integration Points

This dashboard depends on a Prometheus datasource scraping TiKV metrics with consistent `k8s_cluster`, `tidb_cluster`, `instance`, `type`, `result`, and `reason` labels. It integrates specifically with TiKV raw key-value APIs exposed through scheduler command metrics and with the causal timestamp provider metrics exposed by TiKV.

The dashboard can be used beside broader TiKV and PD dashboards. It narrows investigation to raw command latency and timestamp provider activity, which is useful when raw KV workloads or causal timestamp delays are suspected rather than transaction, raftstore, or coprocessor behavior.

## Risks and Edge Cases

- The row panels are collapsed in the export. Users may think the dashboard is empty unless they expand `Read - $command` or `Causal timestamp`.
- `refresh: false` means the dashboard will not auto-refresh unless the user changes the Grafana setting after import.
- The `command` variable regex only includes four raw read command labels. New raw command labels or write-oriented raw commands will be excluded.
- Average latency queries divide `_sum` rate by `_count` rate. If the selected command has no traffic, the expression can return no series or Prometheus special values depending on the datasource behavior.
- Histogram quantiles are aggregated across selected instances, which gives a cluster-level view but can hide per-instance skew.
- The dashboard assumes causal timestamp metric families are present. TiKV builds or versions without these metrics will leave the causal timestamp row empty.
- Short one-minute windows are sensitive to scrape interval, scrape failures, and low traffic.

## Test Signals

Static validation should parse the JSON, verify the two row panels and nine nested graph panels, and check that all sixteen PromQL targets reference `${DS_TEST-CLUSTER}` either directly or through inherited panel configuration. Variable tests should confirm `k8s_cluster`, `tidb_cluster`, `command`, and `instance` all resolve in Prometheus, and that `command` only returns the intended raw command labels.

Runtime validation should expand both rows in Grafana, select a known TiKV instance and raw command, and verify non-empty scheduler command duration, read processing duration, get-ts request, TSO renewal, batch-list counting, and batch-size panels. A regression check should preserve the dashboard UID, variable names, collapsed-row nesting, and the sixteen target expressions unless an intentional dashboard migration changes them.
