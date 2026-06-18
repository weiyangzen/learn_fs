# sources/storage-engines/pebble/internal/compression/adaptive.go

## Purpose
This file implements `AdaptiveCompressor`, a compressor that chooses between a fast and slow compression setting based on sampled relative size reduction.

## Important APIs, Types, And Functions
`AdaptiveCompressor` stores fast/slow compressors, reduction cutoff, sampling frequency, EWMA estimator, RNG, and a reusable buffer. `AdaptiveCompressorParams` configures fast/slow settings, cutoff, sample interval, EWMA half-life, and seed. `NewAdaptiveCompressor`, `Compress`, and `Close` form the API.

## Control Flow
`Compress` reads the current EWMA estimate. If not sampling, it records an unsampled block and chooses fast or slow according to whether the estimate is below the cutoff. If sampling, it compresses with both algorithms, records `1 - slowLen/fastLen`, and returns the fast result if the reduction is too small or the slow result otherwise.

## State And Persistence Behavior
State is per-compressor and in-memory: EWMA history, RNG sequence, and reusable buffer. `Close` closes both child compressors, drops very large buffers, and returns the object to a pool.

## Dependencies And Integration Points
It depends on `ewma.Bytes`, `math/rand/v2`, and the package-level `GetCompressor` abstraction. It is used wherever Pebble wants runtime codec adaptation for blocks.

## Risks And Edge Cases
Risks include biased sampling, bad cutoff selection, using a zero `SampleEvery`, and temporarily storing both fast and slow compressed results. Deterministic seeding is important for tests and reproducibility.

## Test Signals
`adaptive_test.go` checks that random data chooses the fast codec and highly compressible data chooses the slow codec under fixed seeds and parameters.
