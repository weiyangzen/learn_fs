# sources/storage-engines/rocksdb/util/ribbon_test.cc

## Purpose
Provides broad validation and measurement tooling for Ribbon PHSF/filter implementations, configuration tables, seed handling, storage layouts, and false-positive behavior.

## Important APIs, Types, And Functions
The file defines key generators, many `TypesAndSettings` variants, Poisson bound helpers, and tests `CompactnessAndBacktrackAndFpRate`, `Extremes`, `AllowZeroStarts`, `RawAndOrdinalSeeds`, `PhsfBasic`, plus tool-like tests `FindOccupancy` and `OptimizeHomogAtScale`. Optional gflags control thoroughness, occupancy generation, and homogeneous optimization runs.

## Control Flow
The main typed test samples filter sizes, chooses slot counts through `BandingConfigHelper`, builds banding with reseeding, tests rollback by forcing failed adds, optionally adds extra singles/batches, back-substitutes into simple and interleaved solutions, verifies all positives, measures false positives over non-added keys, and compares timing with Bloom queries. Other tests cover zero-key/zero-byte extremes, zero-start behavior, raw/ordinal seed bijection, and general PHSF key-to-value mapping.

## State And Persistence
All state is test-local buffers, counters, generated keys, and optional timing counters. It does not persist artifacts, although `FindOccupancy` prints empirical data used to populate `ribbon_config.cc`.

## Dependencies And Integration Points
Depends on RocksDB hash, coding, Bloom implementation, Ribbon config/impl headers, stopwatch, string utilities, gflags compatibility, and the test harness. It integrates with typed GoogleTest to exercise many compile-time configurations.

## Risks
Many checks are statistical and have configured standard-deviation tolerances, so rare failures are possible. Tool-like tests are bypassed unless flags are set, so occupancy/table regeneration is not part of normal regression runs. Timing output is informational. The test matrix is large but skips full support for coefficient rows smaller than 64 bits in the main compactness test.

## Test Signals
Strong signals include reseed-rate bounds matching configured construction failure chance, rollback leaving occupancy unchanged, no false negatives for added keys, FP counts matching expected simple/interleaved rates with hash-collision correction, interleaved FP rate not lower than simple when it uses a subset of bits, seed translation one-to-one behavior, and correct general PHSF value lookup.
