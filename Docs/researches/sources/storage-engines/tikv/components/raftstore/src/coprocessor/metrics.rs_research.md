# sources/storage-engines/tikv/components/raftstore/src/coprocessor/metrics.rs

## Purpose
`metrics.rs` declares Prometheus metrics for region-size/key observations and region-info collection counts.

## Important APIs, Types, And Functions
`REGION_SIZE_HISTOGRAM` records approximate region sizes with exponential buckets from 1 MiB up to roughly 512 GiB. `REGION_KEYS_HISTOGRAM` records approximate key counts with exponential buckets from 1 to about 2^29. `REGION_COUNT_GAUGE_VEC` exposes a `type` label and is used for `"region"`, `"leader"`, and `"buckets"` counts.

## Control Flow
Metrics are lazy-static globals registered at first use. Size/key split observers call histogram `observe`; `RegionCollector::on_timeout` refreshes the gauge values every 10 seconds.

## State And Persistence Behavior
Metrics are in-process Prometheus collectors only. They are not persisted to raftstore state, but scraping systems may retain time series externally.

## Dependencies And Integration Points
Uses `prometheus` registration macros and is consumed by `split_check/size.rs`, `split_check/keys.rs`, and `region_info_accessor.rs`.

## Risks
Registration uses `unwrap()`, so duplicate metric names or registry failures would panic during initialization. Gauge label cardinality is intentionally tiny; adding dynamic labels would be dangerous. Histogram ranges need to stay aligned with supported region sizes.

## Test Signals
No direct tests. Indirect runtime signal comes from split-check tests invoking histogram observations and region collector timer logic setting gauges.
