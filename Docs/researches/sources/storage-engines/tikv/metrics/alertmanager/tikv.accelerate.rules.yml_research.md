# sources/storage-engines/tikv/metrics/alertmanager/tikv.accelerate.rules.yml

## Purpose
Defines Prometheus recording rules that precompute frequently used TiKV metrics for dashboards and alerts, especially p99/p95 latencies, rates, averages, pending tasks, and per-instance resource signals.

## Important APIs, Types, and Functions
The single group `tikv_accelerate` records derived series such as `tikv_grpc_msg_duration_seconds:p99:1m`, raftstore event and append/apply quantiles, thread CPU rates, engine file averages, PD request averages, coprocessor wait metrics, worker pending/handled task rates, async request failures, and no-grpc CPU variants.

## Control Flow
Prometheus evaluates each `expr` at rule intervals, using `rate`, `sum`, `avg`, `histogram_quantile`, and `avg_over_time` over raw TiKV metrics. Recorded names then serve as faster query inputs elsewhere.

## State and Persistence Behavior
Rules create derived time series in Prometheus storage. They do not affect TiKV runtime behavior.

## Dependencies and Integration Points
Depends on TiKV metric names and labels (`instance`, `type`, `le`, `cf`, `level`, `name`, etc.). Integrated with Prometheus/Alertmanager deployments and Grafana dashboards.

## Risks
Label mismatch or metric renames silently produce empty series. Recording rules without environment/job scoping may aggregate more broadly than intended depending on Prometheus setup. Some expressions use broad `instance=~".*"` selectors, so multi-cluster deployments must isolate rule groups or labels.

## Test Signals
Use `promtool check rules`, query each recorded series in a populated Prometheus, and compare dashboard latency panels against raw histogram expressions after metric changes.
