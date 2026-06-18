# sources/storage-engines/pebble/bench/ycsb.go

## Purpose
`ycsb.go` implements configurable YCSB-like workloads over Pebble, including load, insert, read, scan, reverse-scan, and update operations with Cockroach-style MVCC keys.

## Important APIs, Types, And Functions
Exports are `YCSBConfig`, `DefaultYCSBConfig`, and `RunYCSB`. Internal components include operation constants, `ycsbWeights`, `ycsbParseWorkload`, `ycsbParseKeyDist`, `ycsbBuf`, `ycsb`, `newYcsb`, `init`, `run`, `worker`, `sampleReadAmp`, key/value helpers, operation methods, `tick`, and `done`.

## Control Flow
`RunYCSB` validates wipe/prepopulation, parses workload weights and key distribution, constructs a `ycsb`, and delegates to `RunTest`. `init` bulk-loads initial keys in roughly 1 MiB batches, flushes, then waits for compactions to stabilize. `run` initializes key sequencing, optional read-amp sampling, and workers. Each worker picks operations from weighted distribution, executes the corresponding method, records latency, and exits only when `NumOps` is reached. Inserts coordinate new key visibility with `ackseq` before expanding the key distribution maximum.

## State And Persistence Behavior
The workload writes persistent MVCC-encoded keys with walltime suffixes. `InitialKeys` loads base data; `PrepopulatedKeys` shifts key numbering for fixture reuse. Write options are sync unless WAL is disabled. Read amplification is sampled from iterator metrics or DB metrics. Histograms and counters are in-memory; final output reports read bytes, write bytes including blob activity, read amp, and write amp.

## Dependencies And Integration Points
It depends on Pebble interfaces from `db.go`, `ackseq`, `randvar`, `rate`, histograms, and `RunTest`. `write_bench.go`, `tombstone.go`, and `ycsb_bench_test.go` reuse `newYcsb` and parsing helpers.

## Risks And Edge Cases
Workload parsing rejects zero weights but ignores unknown operation names by leaving weights at zero, which can surprise malformed strings with at least one valid weight. `latest` distribution uses a default skewed-latest generator independent of total keys. Workers are long-running, and fatal DB errors terminate the process. `NumOps` is checked after each operation, so concurrent workers may overshoot slightly.

## Test Signals
Direct tests are in `ycsb_bench_test.go` as an in-process benchmark harness, not unit assertions. Parsing helpers are indirectly tested by workloads using custom configs.
