# sources/storage-engines/pebble/sstable/tablefilters/bloom/simulation.go

## Purpose
Simulates Bloom filter false-positive rates for a given bits/key and probe count, supporting the probe table and documentation.

## Important APIs, Types, And Functions
`SimulateFPR(bitsPerKey, numProbes)` uses `filtersim.SimulateFPR`, random hash collection, `calculateNumLines`, `buildFilter`, `aliasFilterBits`, and `probe`. It returns mean FPR and a formatted string.

## Control Flow
Each run builds a filter for a random size near 10K, probes `cacheLineSize * size` random hashes, subtracts estimated true-positive hash collision contribution, and contributes the result to the aggregate.

## State And Persistence Behavior
No durable state. It builds transient filter bytes for generated documentation.

## Dependencies And Integration Points
Consumed by `simulation_gen.go`. Depends on shared `filtersim` helpers and Bloom internals.

## Risks And Edge Cases
The simulation assumes uniform random 32-bit hashes and estimates true positives from hash-space collision probability. It is CPU-heavy but not used in normal builds.

## Test Signals
Printed lines and the generated simulation markdown table are the primary signals.
