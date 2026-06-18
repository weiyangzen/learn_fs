# sources/object-store/rustfs/crates/obs/src/metrics/collectors/request.rs

Purpose: converts API request snapshots into labeled metrics for request counts, in-flight requests, errors, cancellations, TTFB distribution buckets, and traffic bytes.

Important APIs/types: `ApiRequestStats` carries endpoint `name`, request `req_type`, counts, `ttfb_distribution: Vec<(String, f64)>`, and sent/received bytes. `collect_request_metrics(&[ApiRequestStats])` emits per-endpoint metrics.

Control flow: iterates stats, emitting six metrics labeled by `name` and `type`, then one TTFB distribution metric per `(le,value)` labeled by `name`, `type`, and `le`, then traffic sent/received metrics labeled only by `type`.

State/persistence: pure conversion. Request counters/latency buckets are maintained by API instrumentation outside this file.

Dependencies/integration: uses `schema::request` descriptors. This collector is exported by `collectors/mod.rs`; it is not directly visible in the shown scheduler tasks, so it may be used by HTTP handlers or another scrape path.

Risks: traffic metrics omit the API `name` label while request counters include it; this is intentional if traffic is aggregated by type but can surprise dashboards. Histogram/distribution values are reported through descriptor type semantics, so callers must pass cumulative bucket values if Prometheus histogram expectations apply.

Test signals: tests check a one-endpoint output count of twelve, exact total and in-flight values, `report_metrics` compatibility, and empty input behavior.
