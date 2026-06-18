# sources/storage-engines/pebble/internal/randvar/uniform.go

## Purpose
This file implements `randvar.Uniform`, a tiny random variable generator for inclusive uniform draws over a mutable integer range. It is used where Pebble tests or benchmarks need a distribution whose upper bound can grow over time without replacing the generator.

## Important APIs, Types, and Functions
`Uniform` stores an immutable `min uint64` and an atomically mutable `max`. `NewUniform(min, max)` initializes the generator and relies on the caller to preserve `min <= max`. `IncMax(delta)` atomically increases the upper bound. `Max()` reads the current bound. `Uint64(rng *rand.Rand)` returns `rng.Uint64N(Max()-min+1)+min`, so the range is inclusive at both ends.

## Control Flow and State
The control flow is direct: construction stores `max`, updates call `atomic.Uint64.Add`, and draws load `max` then call the supplied RNG. There is no persistence. The only shared state is `max`, made race-safe for concurrent increments and readers. The `rng` itself is supplied by the caller and is not protected by this type.

## Dependencies and Integration
The file depends on Go's `math/rand/v2` and `sync/atomic`. It follows the same `IncMax`, `Max`, and `Uint64` shape as `Zipf`, allowing test generators to switch between distributions.

## Risks and Edge Cases
The constructor does not validate `min <= max`; if violated, `Max()-min+1` underflows and produces an unintended wide range. `IncMax` can overflow `uint64` if abused. Passing a nil RNG will panic because this type does not call `ensureRand`, unlike `Weighted`.

## Test Signals
There is no direct test file for `Uniform` in this work item. Coverage is likely indirect through consumers. Useful missing tests would check inclusive endpoints, increasing `Max`, and invalid constructor behavior if the contract changes.
