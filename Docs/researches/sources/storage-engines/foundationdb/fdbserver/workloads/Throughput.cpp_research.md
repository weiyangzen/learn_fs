# sources/storage-engines/foundationdb/fdbserver/workloads/Throughput.cpp

## Purpose
`ThroughputWorkload` is an adaptive throughput benchmark. It generates configurable read/write transactions, adjusts actor fan-out to target a latency, and records operation throughput plus latency distributions.

## Important APIs, Types, and Functions
The source defines `ITransactor::Stats`, `RWTransactor`, `ABTransactor`, `SweepTransactor`, `IMeasurer`, `MeasureSinglePeriod`, `MeasurePeriodically`, `MeasureMulti`, and `ThroughputWorkload`. It uses `Transaction`, `actorCollection()`, `PromiseStream<Future<Void>>`, `DDSketch`, `PerfMetric`, and deterministic key/value generators.

## Control Flow
The constructor builds A and B transaction types from workload options, chooses either an `ABTransactor` mixture or a time-based `SweepTransactor`, configures one required measurement period and optional periodic measurements, and calculates total duration. `start()` starts the measurer and an actor collection, seeds it with one `throughputActor()`, and times out after the measurement window. Each actor performs one transaction, records latency and stats, updates proportional/integral control terms, computes desired successors, and sends successor actors into the collection.

## State and Persistence Behavior
Database state is random writes to generated fixed-width keys. Runtime state includes adaptive actor count, latency integrals, measurement accumulators, and transaction stats. There is no setup; the workload expects any desired preloading to come from a separate workload.

## Dependencies and Integration Points
It integrates with Native API transactions, actor collection scheduling, DDSketch, tester metrics, deterministic random generation, and workload configuration. It includes worker-interface headers but primarily uses client transaction APIs.

## Risks and Edge Cases
`RWTransactor::rowReadLatency` divides by `reads`; read count zero would be invalid. `Stats::totalLatency` is set by the outer actor after transaction completion, while GRV/row/commit latency are filled by the transactor. The adaptive controller is per client and may diverge across clients, which the code notes. Actor fan-out is capped but can still create high load.

## Test Signals
The workload always passes `check()`. Metrics include transactions/sec, retries/sec, operations/sec, read/write rows/sec, total latency percentiles, row-read latency, GRV latency, commit latency, and optional time-prefixed periodic metrics.
