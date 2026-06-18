# sources/storage-engines/foundationdb/fdbserver/workloads/WriteBandwidth.cpp

## Purpose
`WriteBandwidthWorkload` bulk-loads a keyspace and then measures write transaction throughput, write rows/sec, bytes/sec, GRV latency, and commit latency for batched writes.

## Important APIs, Types, and Functions
The workload derives from `KVWorkload`, uses `bulkSetup()`, `Transaction::getReadVersion()`, `addWriteConflictRange()`, `Transaction::set(..., AddConflictRange::False)`, `DDSketch`, `PerfIntCounter`, and KVWorkload key/value generation. Key methods are `setup()`, `start()`, and `writeClient()`.

## Control Flow
`setup()` bulk-loads `nodeCount` keys with optional warmup and max insert rate, capturing load time through a promise. `start()` launches `actorCount` write clients and waits for either all clients or `testDuration`. Each client repeatedly chooses a random contiguous key span of `keysPerTransaction`, gets a read version and records GRV latency, adds one explicit write conflict range covering the span, writes each key with a random value without per-key conflict ranges, commits, records commit latency, increments retries on errors, and counts transactions.

## State and Persistence Behavior
Database state is the KVWorkload keyspace, repeatedly overwritten in random contiguous batches. Runtime state is transaction/retry counters, load time, and latency sketches. There is no final data correctness check.

## Dependencies and Integration Points
It integrates with KVWorkload setup, Native API conflict range behavior, DDSketch metrics, and tester workload options for actor count, key/value sizes, warmup, and insert rate.

## Risks and Edge Cases
`startIdx` calculation assumes `nodeCount > keysPerTransaction`; otherwise random span selection can underflow or produce invalid ranges. Since writes disable per-key conflict ranges and add one explicit range, the workload specifically measures a conflict-range optimization path. `check()` always returns true.

## Test Signals
Metrics include measured duration, transactions/sec, operations/sec, rows, bytes written/sec, load time, retries, and GRV/commit latency percentiles. Retried transaction errors increment the retry counter.
