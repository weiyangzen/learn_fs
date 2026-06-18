# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/StorageMetrics.h

## Purpose
`StorageMetrics.h` declares storage-server metric sampling, wait-metrics notification, range splitting, read-hot-range reporting, and generic serving loops for storage metrics RPCs.

## Important APIs, Types, And Functions
It defines histogram names, `StorageMetricSample`, `TransientStorageMetricSample`, `WaitMetricsMapHighWatermarks`, `StorageServerMetrics`, `ByteSampleInfo`, `isKeyValueInSample`, `CommonStorageCounters`, and `IStorageMetricsService`. `StorageServerMetrics` exposes metric estimation, notifications for reads/writes/not-readable ranges, polling, split metrics, storage metrics replies, wait metrics, read-hot ranges, hot shard counts, and split points. `serveStorageMetricsRequests` races request-serving coroutines and polling.

## Control Flow
Storage server code records sampled byte/read/write metrics by key, expires transient samples, notifies waiters in a `KeyRangeMap`, and serves request streams from `StorageServerInterface`. Split and hot-range methods use samples to choose keys or ranges.

## State And Persistence Behavior
Metrics are in-memory and approximate. They affect durable DD decisions indirectly by driving shard splits, merges, movement, and throttling.

## Dependencies And Integration Points
It depends on FDB types, simulator, unit tests, storage-server interfaces, key range maps, server knobs, Flow counters, and request streams. It integrates with storage servers, DD, ratekeeper, fetchKeys, and status/metrics.

## Risks And Edge Cases
Sampling probability invariants, high-watcher wait maps, stale transient samples, empty/not-readable ranges, and split-key math are risky. Knob-dependent units must stay consistent with storage and DD expectations.

## Test Signals
Tests should cover byte-sample probability/estimation, waitMetrics notification and timeout behavior, split points, hot-range detection, high-watermark tracing, and service loops handling each request stream.
