# sources/storage-engines/pebble/internal/randvar/weighted.go

## Purpose
This file provides `randvar.Weighted`, a simple discrete weighted random generator over indexes `[0,len(weights)-1]`. It is intended for tests and workload generators that need categorical selection according to relative floating-point weights.

## Important APIs, Types, and Functions
`Weighted` holds an RNG, the precomputed sum of weights, and the original weight slice. `NewWeighted(rng, weights...)` computes the sum and replaces nil RNGs through package helper `ensureRand`. `Int()` draws a point `p` in `[0,sum)` and linearly scans weights until the cumulative bucket is found, returning the last index as a fallback for rounding.

## Control Flow and State
Construction is one pass over the weights. Every draw is another pass over the slice, subtracting each weight from `p`. The generator does not copy `weights`, so callers mutating the backing slice after construction can change draw behavior without updating `sum`. There is no persistence and no synchronization.

## Dependencies and Integration
The only direct external dependency is `math/rand/v2`; package-local `ensureRand` supplies a default RNG. It integrates with the rest of `internal/randvar` as a convenience distribution alongside Zipf, uniform, deck, and skewed-latest generators.

## Risks and Edge Cases
Zero and negative weights are not rejected. A zero weight can still be selected if `p <= weight` when `p` is exactly zero, although that is rare. Negative weights distort the subtraction logic. An empty `weights` slice causes `Int` to return `-1`. A zero total sum makes all draws use `p == 0` and typically returns the first non-negative bucket. None of these are guarded, so callers must provide sane weights.

## Test Signals
`weighted_test.go` creates a generator with weights `1,2,2,0,3` and draws 10,000 samples, only dumping output in verbose mode. It exercises construction and repeated draws but has no assertions about probabilities, zero-weight behavior, empty input, or invalid weights.
