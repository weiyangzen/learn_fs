# sources/storage-engines/tikv/components/pd_client/src/metrics.rs

Purpose: Registers all Prometheus metrics used by the PD client crate. The file centralizes request latency, reconnect status, heartbeat/bucket reporting, store size, region traffic histograms, request forwarding, and pending TSO counters.

Important APIs/types/functions: `make_static_metric!` creates label enums `PDRequestEventType`, `PDReconnectEventKind`, and `StoreSizeEventType`, plus statically typed metric vectors `StoreSizeEventIntrVec`, `PDRequestEventHistogramVec`, and `PDReconnectEventCounterVec`. `lazy_static!` exports `PD_REQUEST_HISTOGRAM_VEC`, `PD_HEARTBEAT_COUNTER_VEC`, `PD_BUCKETS_COUNTER_VEC`, `PD_RECONNECT_COUNTER_VEC`, `PD_PENDING_HEARTBEAT_GAUGE`, `PD_PENDING_BUCKETS_GAUGE`, `PD_VALIDATE_PEER_COUNTER_VEC`, `STORE_SIZE_EVENT_INT_VEC`, region read/write histograms, `REQUEST_FORWARDED_GAUGE_VEC`, and `PD_PENDING_TSO_REQUEST_GAUGE`.

Control flow: There is no runtime control flow beyond lazy initialization. Metrics register on first access and unwrap registration failures, matching TiKV's expectation that metric names are unique process-wide.

State and persistence behavior: The only state is in Prometheus collectors held in global statics. Nothing is persisted. Counters and gauges are process-lifetime observability state, reset on restart.

Dependencies and integration points: The file uses `prometheus`, `prometheus_static_metric`, and `lazy_static`. It is integrated by `pd_client::util` for request durations, reconnect outcomes, forwarded-host gauges, heartbeat/bucket pending gauges, and by `pd_client::tso` for pending timestamp request counts.

Risks: Metric name or label changes affect dashboards and alerting. `unwrap()` on registration can panic if another crate registers the same metric name. Some histogram descriptions appear copy-pasted, for example read histograms say "written" in help text; this is low functional risk but can confuse operators.

Test signals: No local unit tests. Validation normally comes from compile-time label generation and runtime metric registration during PD client tests or full TiKV startup.
