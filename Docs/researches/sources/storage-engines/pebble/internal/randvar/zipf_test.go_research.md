# sources/storage-engines/pebble/internal/randvar/zipf_test.go

## Purpose
This file tests the Zipf generator's zeta computations, incremental max extension, accepted parameter range, and basic sampling path.

## Important APIs, Types, and Functions
`TestZeta` verifies `computeZetaFromScratch` and `computeZetaIncrementally` against fixed expected values for theta `0.99`. `TestZetaIncMax` builds `[0,10]` by starting at `[0,0]` and calling `IncMax(1)` ten times, then compares `zetaN` and `eta` with a directly constructed `[0,10]` generator. `TestNewZipf` asserts construction succeeds for theta `0.99` and `1.01`. `TestZipf` draws 10,000 values and optionally dumps samples.

## Control Flow and State
The tests directly lock the generator internals for deterministic state comparison. Sampling is non-assertive and uses `NewRand`, a package helper outside this source list. No persistent state is involved.

## Dependencies and Integration
The file imports `math`, `testing`, and `testify/require`. It uses package-private functions and fields because it is in package `randvar`, making it able to validate internal cached constants.

## Risks and Gaps
The long zeta test for `n=100000000` is intentionally disabled because it is slow. Invalid parameter tests are missing for `min > max`, negative theta, and theta exactly one. Sampling tests do not check support bounds or statistical shape beyond avoiding panics.

## Test Signals
The strongest signal is that incremental zeta maintenance is intended to be exactly equivalent to recomputation for growing maxima. The accepted theta cases show sub-unity and super-unity theta values are supported.
