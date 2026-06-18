# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/simulation.go

## Purpose
Runs probabilistic simulations for binary fuse filter false-positive rates and average bits per key for documentation and tuning.

## Important APIs, Types, And Functions
`SimulateFPR(avgSize, fpBits)` returns mean FPR, standard deviation, and average bits per key. It uses `filtersim.SimulateFPR`, random 64-bit hashes, `hashCollector`, `buildFilter`, `mayContain`, and atomic counters for aggregate key/filter bytes.

## Control Flow
For each run, the simulation chooses a set size near `avgSize`, builds a filter for random hashes, performs `10000 * 2^fpBits` random non-member probes, computes the positive rate, and accumulates bytes/key. It prints a human-readable summary.

## State And Persistence Behavior
No persisted state. It constructs transient filters and collectors for generated documentation. Atomic counters coordinate concurrent simulation workers.

## Dependencies And Integration Points
Depends on `filtersim`, `crhumanize`, random number generation, and binary fuse build/probe internals. `simulation_gen.go` consumes it to produce `simulation.md`.

## Risks And Edge Cases
If filter construction fails, the simulation panics because documentation generation expects valid parameter combinations. The random model uses uniformly distributed hashes and may not reflect pathological real key distributions beyond the hash function.

## Test Signals
The output FPR table is the signal; it supports comments in the policy file but is not part of normal tests.
