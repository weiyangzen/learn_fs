# sources/storage-engines/foundationdb/fdbserver/workloads/MinimumThroughput.cpp

## Purpose
Simple throughput floor workload for error-free conditions. It verifies the cluster can sustain a configured rate of basic point reads and optional writes.

## Important APIs, types, and functions
`MinimumThroughputWorkload` tracks actors, node count, duration, per-client target TPS, minimum expected TPS, read fraction, client futures, transaction/retry counters, and latency. `keyForIndex` uses `MTP/%08d`; `client` performs the workload loop.

## Control flow
Every client starts `actorCount` Poisson-paced actors for `testDuration`. Each operation picks a random key, chooses read-only versus read-write, reads the key, optionally writes `"x"` and commits, then records transaction count and latency. Check reports client errors and fails if achieved transactions are below `testDuration * minExpectedTransactionsPerSecond`.

## State and persistence behavior
Writes are simple point sets under `MTP/` keys. There is no setup or cleanup, and absent keys are valid for read-only operations.

## Dependencies and integration points
Depends on normal transaction get/set/commit paths, retry handling, tester pacing, and perf metrics. It disables all failure injection to keep the throughput assertion meaningful.

## Risks and test signals
The workload is sensitive to configured expected rate and environment capacity. Division by zero is possible in average latency metric if no transactions complete. Signals are client errors, throughput-below-minimum trace details, transaction/retry counters, and average latency.
