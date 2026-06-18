# sources/storage-engines/pebble/bench/scan.go

## Purpose
`scan.go` implements a DB-backed scan benchmark over Cockroach-style MVCC keys, measuring row throughput, byte throughput, and per-row latency for forward or reverse scans.

## Important APIs, Types, And Functions
`ScanConfig`, `DefaultScanConfig`, and `RunScan` are the exposed surfaces. Config controls reverse scanning, row-count distribution, and value-size distribution.

## Control Flow
`RunScan` preloads 100,000 MVCC keys in batches of 1,000, commits and flushes them, then starts `common.Concurrency` workers. Each worker picks a random start index and row count, encodes start/end keys, calls `mvccForwardScan` or `mvccReverseScan`, validates the scanned count, and atomically accumulates bytes and rows. Tick/done callbacks print instantaneous and cumulative rates.

## State And Persistence Behavior
Initialization writes and flushes a fixed keyspace. The run phase is read-only and repeatedly opens iterators through MVCC scan helpers. WAL sync mode for preload follows `DisableWAL`.

## Dependencies And Integration Points
It uses `RunTest`, the `DB` abstraction, `cockroachkvs`, `randvar`, `mvcc.go` scan helpers, and atomic counters.

## Risks And Edge Cases
The benchmark assumes row distributions never exceed the fixed key count; invalid distributions can panic or fatal on mismatched counts. Workers run indefinitely until the outer harness stops. The use of deterministic RNG seeds by worker index improves reproducibility but can create correlated patterns if concurrency changes.

## Test Signals
No direct tests. Runtime fatal count checks and benchmark output are the main validation signals.
