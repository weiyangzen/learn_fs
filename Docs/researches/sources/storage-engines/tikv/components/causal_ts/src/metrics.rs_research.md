# sources/storage-engines/tikv/components/causal_ts/src/metrics.rs

## Purpose
Defines prometheus metrics for timestamp provider cache size, request latency, renew latency, and batch-list counts.

## APIs, Types, And Functions
Global collectors include `TS_PROVIDER_TSO_BATCH_SIZE`, `TS_PROVIDER_GET_TS_DURATION`, `TS_PROVIDER_TSO_BATCH_RENEW_DURATION`, and `TS_PROVIDER_TSO_BATCH_LIST_COUNTING`. Static labels include renew reasons `init`, `background`, `used_up`, `flush`; counting kinds `tso_usage`, `tso_remain`, `new_batch_size`; and result kinds `ok`/`err`. `From<&Result>` converts success/failure to metric labels.

## Control Flow
Provider code observes get-ts and renew durations, reports usage/remain/new batch sizes, and sets total batch size after renew attempts.

## State And Persistence
Metrics live in prometheus collectors and are exported by the process. No durable state is written.

## Dependencies And Integration Points
Uses `prometheus`, `prometheus_static_metric`, and `lazy_static`. `tso.rs` is the primary consumer.

## Risks And Test Signals
Metric names and labels are operational interfaces. Histograms cover very small get-ts latencies and long renew durations, matching cache-fast-path and PD-slow-path expectations.
