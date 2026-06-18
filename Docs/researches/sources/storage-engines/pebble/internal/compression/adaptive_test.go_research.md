# sources/storage-engines/pebble/internal/compression/adaptive_test.go

## Purpose
This file tests adaptive compression decisions on incompressible and compressible workloads.

## Important APIs, Types, And Functions
`TestAdaptiveCompressorRand` configures fast MinLZ and slow Zstd with a 20% cutoff. `TestAdaptiveCompressorCompressible` configures no compression versus Zstd with a 60% cutoff.

## Control Flow
Each test creates an adaptive compressor with fixed sampling seed, repeatedly builds payloads, calls `Compress`, and asserts the returned `Setting`. Random payloads are expected to choose `MinLZFastest`; patterned payloads are expected to choose `ZstdLevel1`.

## State And Persistence Behavior
Only compressor EWMA/RNG state changes. No persistent artifacts are created.

## Dependencies And Integration Points
The tests depend on `math/rand/v2`, `testify/require`, MinLZ, Zstd, no-compression settings, and `AdaptiveCompressor`.

## Risks And Edge Cases
Tests rely on deterministic seeds and payload generation. They validate clear cases, not borderline cutoffs, zero/invalid sampling parameters, or close/reuse pooling behavior.

## Test Signals
Consistent returned settings across 100 iterations indicate the estimator and sampling path converge to the expected fast or slow choice.
