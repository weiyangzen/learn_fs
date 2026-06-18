# sources/storage-engines/tikv/metrics/grafana/common.py

## Purpose
Provides shared Python helpers for generating TiKV Grafana dashboards with `grafanalib`. It centralizes Prometheus expression construction, dashboard variables, target creation, panel layout, graph/time-series/stat/table/heatmap panel factories, legends, axes, series overrides, and histogram panel patterns.

## Important APIs, Types, and Functions
Constants define Prometheus datasource input and Grafana variables. `Expr` models PromQL aggregation/function/selectors/range/by/extra clauses, with mutation helpers for aggregation, functions, extra expression text, default instance skipping, and group-by extension. `OpExpr` combines expressions with binary operators. Helper functions include `expr_sum`, `expr_avg`, `expr_max`, `expr_min`, `expr_sum_rate`, `expr_sum_delta`, `expr_sum_increase`, `expr_histogram_quantile`, `expr_topk`, `expr_histogram_avg`, `target`, `template`, `Layout`, `timeseries_panel`, `yaxis`, `yaxes`, `graph_legend`, `graph_panel`, `series_override`, `heatmap_panel`, `stat_panel`, `graph_panel_histogram_quantiles`, histogram heatmap/graph pair creation, and `table_panel`.

## Control Flow
Dashboard modules build `Expr` objects, convert them to strings when constructing `Target`s, and then pass targets into panel factories. `Layout.row` assigns Grafana grid positions. Histogram helpers derive `_bucket`, `_sum`, and `_count` series from a base metric. Panel helpers patch grafanalib JSON where needed, such as graph fill gradients, series override fields, heatmap options, and table transformations.

## State and Persistence Behavior
No external persistence. Many helpers mutate object instances in place: `Expr.aggregate`, `Expr.function`, `Expr.extra`, `append_by_labels`, `target(additional_groupby=True)`, and y-axis decimal assignment change existing objects. Generated dashboard JSON is the durable artifact outside this file.

## Dependencies and Integration Points
Depends on `attrs`, `grafanalib.core`, and `grafanalib.formatunits`. Integrates with TiKV dashboard generator modules, Prometheus labels (`k8s_cluster`, `tidb_cluster`, `instance`), Grafana templating, and recorded/raw metrics from the alert rule files.

## Risks
Several defaults are mutable lists (`label_selectors=[]`, `by_labels=["instance"]`, panel override defaults), which can leak mutations between calls if modified. `Expr` methods mutate and return `self`, so reusing expression objects can unintentionally alter earlier targets. String-built PromQL has limited validation beyond selector assertions. `target(additional_groupby=True)` assumes a legend format is present for some paths.

## Test Signals
Generate dashboards and validate JSON with grafanalib/Grafana import checks. Unit-test representative PromQL strings, histogram suffix assertions, additional group-by legend changes, layout grid positions, table target instant mode, and series override JSON patches.
