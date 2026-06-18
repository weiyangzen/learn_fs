# sources/storage-engines/pebble/bench/histogram.go

## Purpose
`histogram.go` provides concurrent latency histograms and registry-level periodic/cumulative aggregation for benchmark reporting.

## Important APIs, Types, And Functions
`newHistogram`, `namedHistogram`, `newNamedHistogram`, `Record`, `tick`, `histogramTick`, `histogramRegistry`, `newHistogramRegistry`, `Register`, and `Tick` are the core pieces. Latency range is clamped from 10 microseconds to 10 seconds.

## Control Flow
Workers call `Record`, which clamps duration and records under a mutex. Reporting calls `histogramRegistry.Tick`, snapshots the registered histograms, rotates each current histogram, merges by name, updates cumulative histograms and previous tick timestamps, then invokes the caller's formatting callback in sorted name order.

## State And Persistence Behavior
All state is in-memory. `namedHistogram` protects current interval histograms with a mutex. The registry stores cumulative histograms and previous tick times by name. Nothing is persisted except printed benchmark output produced by callers.

## Dependencies And Integration Points
It depends on `HdrHistogram`, `sync`, `sort`, and Cockroach errors. Most benchmark workloads register operation-specific histograms through this registry.

## Risks And Edge Cases
If a duration still records outside the clamped range, the code panics because that indicates an invariant violation. Empty tick intervals can produce zero counts, and callers must avoid divide-by-zero if no operations occurred. Multiple workers sharing the same histogram name are intentionally merged.

## Test Signals
No direct tests. Indirect signal comes from benchmark output and workload tests that call reporting paths.
