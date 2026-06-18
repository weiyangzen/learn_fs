# sources/storage-engines/tikv/metrics/alertmanager/tikv.rules.yml

## Purpose
Defines TiKV alerting rules for critical, emergency, and warning operational conditions such as critical errors, memory growth, GC failure, network/report failures, channel full, write stalls, Raft lag, slow async requests, CPU saturation, pending tasks, low disk space, restarts, and quota pressure.

## Important APIs, Types, and Functions
The `alert.rules` group contains alert entries with PromQL `expr`, optional `for`, labels including `env`, `level`, and duplicated `expr`, and annotations with templated descriptions, values, and summaries. Metrics include TiKV critical errors, process memory, GC worker counters, raftstore histograms, scheduler/coprocessor metrics, worker pending tasks, store size, process start time, and TiDB client GC results.

## Control Flow
Prometheus evaluates each expression; if it remains true for the configured `for` duration, Alertmanager receives a firing alert with labels and annotations. Several critical alerts fire after one minute; the critical-error alert intentionally has no `for` clause.

## State and Persistence Behavior
The file creates alert state in Prometheus/Alertmanager but does not mutate TiKV. Alert state persists according to Prometheus evaluation history and Alertmanager grouping/silencing.

## Dependencies and Integration Points
Depends on stable metric names and labels exported by TiKV, TiDB clients, and process exporters. `ENV_LABELS_ENV` is a deployment-time placeholder. Integrates with Alertmanager routing and on-call runbooks.

## Risks
PromQL typos or stale metric names can disable alerts; for example exact label regex and metric spelling must match exporters. Hard-coded thresholds may be noisy or blind for clusters of different sizes. Broad selectors can cross cluster boundaries if environment labels are not templated correctly.

## Test Signals
Run `promtool check rules`, execute expressions in staging Prometheus, verify alert routing with sample labels, and review historical firing frequency after threshold changes. Add metric-rename checks when TiKV instrumentation changes.
