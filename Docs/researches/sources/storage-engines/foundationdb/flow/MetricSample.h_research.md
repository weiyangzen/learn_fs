# sources/storage-engines/foundationdb/flow/MetricSample.h

## Purpose
Defines sampled transient metric containers backed by `IndexedSet`, including expiration queues and threshold-crossing tracking.

## Important APIs, Types, And Functions
`MetricSample<T>` stores `IndexedSet<T, int64_t> sample`, `metricUnitsPerSample`, and `getMetric()`. `TransientMetricSample<T>` adds an expiration queue plus `addAndExpire()` and `poll()`. `TransientThresholdMetricSample<T>` adds `thresholdCrossedSet`, `thresholdLimit`, `isAboveThreshold()`, templated `addAndExpire()`, and `poll()`.

## Control Flow
Adds with magnitude below `metricUnitsPerSample` are probabilistically rounded to one sampling unit using nondeterministic random. Nonzero sampled deltas update the metric set and enqueue an inverse delta at expiration time. `poll()` expires queued deltas in time order, updates/removes sample entries, and in the threshold variant removes threshold markers when values fall back below the limit.

## State And Persistence Behavior
All state is in-memory: current sampled metrics, expiration queues, and threshold-crossed keys. Uses `now()` for expiration decisions.

## Dependencies And Integration Points
Requires `IndexedSet`, `Deque`, `now()`, assertions, and nondeterministic random from Flow includes. It is suitable for TraceEvent throttling/metric sampling features where exact per-key accounting is too expensive.

## Risks And Edge Cases
Sampling is probabilistic and not deterministic. Queue entries copy keys from the set; key lifetime and copy cost matter. Correctness assumes expirations are polled regularly and in chronological insertion order. Threshold transitions use assertions to maintain crossed-set consistency.

## Test Signals
No local tests. Indirect signal comes from metric/throttling tests and any invariant failures in threshold tracking.
