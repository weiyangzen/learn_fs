# sources/storage-engines/foundationdb/fdbserver/workloads/StreamingRead.cpp

## Purpose
`StreamingReadWorkload` is a read throughput and latency workload that scans or randomly reads ranges over a bulk-loaded keyspace. It measures keys read, bytes read, and transaction latency distribution for range reads.

## Important APIs, Types, and Functions
The workload derives from `TestWorkload`, registers as `StreamingRead`, and uses `bulkSetup()`, `Transaction::getRange()`, `DDSketch<double>`, `PerfIntCounter`, and `PerfMetric`. Helpers include `keyForIndex()`, `operator()`, and `streamingReadClient()`.

## Control Flow
The constructor configures actor count, key/value sizes, reads and ranges per transaction, node count, warmup, and sequential-vs-random mode. `setup()` bulk-loads deterministic keys with a constant value. `start()` distributes actor IDs across clients and waits for timed `streamingReadClient()` actors. Each actor calculates its key partition, repeatedly opens a transaction, performs up to `rangesPerTransaction` range reads or stops after roughly three seconds inside one transaction, updates byte/key counters, records latency, and increments transaction count.

## State and Persistence Behavior
Database state is read-only after setup. Runtime state consists of counters, latency sketch samples, and per-actor `currentIndex` for sequential scanning. Sequential mode partitions the logical keyspace by actor; random mode reads anywhere in the full `nodeCount` range.

## Dependencies and Integration Points
This workload integrates with the tester workload factory, bulk setup, Native API range reads, deterministic key encoding via `emplaceIndex()`, and DDSketch percentile metrics.

## Risks and Edge Cases
The workload does not validate returned keys against expected values, so it measures read API behavior but does not directly prove data correctness. `rangeSize` is rounded and final range size can differ from earlier ranges. Very low or mismatched `readsPerTransaction` and `rangesPerTransaction` settings can produce small or zero final ranges. Metrics divide by `testDuration`, not actual elapsed actor time.

## Test Signals
Metrics are the main output: transactions, keys read, bytes read per second, and mean/median/90th/98th percentile latencies. `check()` returns true after clearing client futures.
