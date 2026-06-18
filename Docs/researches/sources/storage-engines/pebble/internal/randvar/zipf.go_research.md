# sources/storage-engines/pebble/internal/randvar/zipf.go

## Purpose
This file implements an incrementally extensible Zipfian random variable generator derived from the YCSB-style "Incrementing Zipfian Random Number Generator." It supports `theta` values below 1, unlike Go's standard Zipf implementation, and can grow `max` without recomputing all hidden constants from scratch.

## Important APIs, Types, and Functions
`Zipf` stores immutable parameters `theta` and `min`, derived constants `alpha`, `zeta2`, and `halfPowTheta`, and mutable `max`, `eta`, and `zetaN` behind an embedded RW mutex. `NewDefaultZipf()` uses YCSB-like defaults. `NewZipf(min,max,theta)` validates `min <= max` and rejects `theta < 0` and `theta == 1`, computes zeta constants, and initializes `eta`. `IncMax(delta)` extends the support and updates `zetaN` incrementally. `Max()` reads the current max. `Uint64(rng)` samples the distribution using the cached constants. Helpers compute zeta from scratch or incrementally, including a precomputed default for the 10-billion-key default case.

## Control Flow and State
Construction computes `zeta2`, `halfPowTheta`, `zetaN`, `alpha`, and `eta` once. `IncMax` locks the mutable state, increments `max`, recomputes only the additional zeta terms, and refreshes `eta`. `Uint64` draws a uniform float, holds an RLock while reading mutable distribution constants, and maps the draw through the Zipf inversion formula. There is no disk persistence; the distribution state is memory resident and reproducible only through constructor parameters and mutation history.

## Dependencies and Integration
The file uses `math`, `math/rand/v2`, `sync`, and `github.com/cockroachdb/errors`. It integrates with Pebble workload/test random generators that need a growing key universe, especially YCSB-like workloads.

## Risks and Edge Cases
The error message says `0 < theta`, but the code allows `theta == 0`; that may be intentional for uniform-like behavior or a stale message. `Max()` uses an exclusive lock rather than an RLock, which is correct but less concurrent than necessary. `IncMax` does not guard overflow of `max`. `Uint64` requires non-nil RNG and trusts floating-point arithmetic; extreme parameters may be sensitive to precision. The default zeta shortcut is exact only for the known default tuple.

## Test Signals
`zipf_test.go` checks zeta values against known constants, verifies incremental `IncMax` matches constructor-computed state, accepts representative theta values below and above 1, and smoke-tests sampling. The tests do not assert sampled distribution frequencies, concurrency behavior, or boundary rejection for invalid parameters.
