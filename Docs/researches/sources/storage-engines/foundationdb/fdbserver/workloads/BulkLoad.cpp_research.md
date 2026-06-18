# sources/storage-engines/foundationdb/fdbserver/workloads/BulkLoad.cpp

## Purpose
`BulkLoad.cpp` defines a lightweight throughput workload named `BulkLoad`. It is not the metadata-driven bulk loading test; instead it continuously writes formatted keys and fixed-size values with many actors to measure raw write throughput, retries, and latency.

## Important APIs, Types, And Functions
The main type is `BulkLoadWorkload : TestWorkload`, registered by `WorkloadFactory<BulkLoadWorkload>`. It uses `Transaction`, `tr.set`, `tr.makeSelfConflicting`, `tr.getReadVersion`, `tr.commit`, `tr.onError`, `timeout`, `waitForAll`, `PerfIntCounter`, and `DDSketch<double>` for latency statistics.

## Control Flow
The constructor reads `testDuration`, `actorCount`, `writesPerTransaction`, `valueBytes`, `targetBytes`, and `keyPrefix`. `start` launches `actorCount` `bulkLoadClient` actors per tester client, each bounded by `testDuration`. Each actor repeatedly constructs a transaction containing `writesPerTransaction` sequential keys under `keyPrefix/bulkload/<client>/<actor>/<idx>`, makes the transaction self-conflicting, obtains a read version, commits, records latency and counters, and stops once its share of `targetBytes` has been exceeded.

## State And Persistence
Persistent state is user key data under the configured prefix. Runtime state is counters, retry counts, DDSketch samples, per-actor `idx`, and per-actor `totalBytes`. `check` clears the retained future vector but does not validate or remove written keys.

## Dependencies And Integration Points
The workload depends on the native client API, tester workload registration, `fdbrpc/DDSketch.h`, and FDB transaction conflict/read-version behavior. The formatted key pattern makes it easy to isolate throughput data by client and actor.

## Risks
The `targetBytes` comparison divides by `clientCount * actorCount`, so unusual zero/invalid option values would be unsafe, though defaults are positive. `valueBytes` is forced to at least 16 but metrics approximate bytes as `valueBytes + 16`, which does not include the full formatted key length. There is no correctness check for all expected rows, so failures are observed through transaction errors, retries, timeout, and metrics rather than data reconciliation.

## Test Signals
Metrics include transactions, retries, rows written, transactions/sec, rows/sec, keys/sec, bytes/sec, mean latency, median latency, 90th percentile, and 98th percentile. High retry counts or low throughput are the main workload-level signals.
