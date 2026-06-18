# sources/storage-engines/rocksdb/util/random.h

## Purpose
Defines several non-cryptographic random utilities: a LevelDB-style deterministic linear congruential generator, wrappers around `std::mt19937` and `std::mt19937_64`, and seeded shuffle helpers.

## Important APIs, Types, And Functions
`Random` exposes `Next`, `Next64`, `Uniform`, `OneIn`, `OneInOpt`, `PercentTrue`, `Skewed`, string generators, `Reset`, and `GetTLSInstance`. `Random32` wraps `std::mt19937` with exact `Next`, uniform distribution, faster approximate `Uniformish`, `OneIn`, `Skewed`, and reseeding. `Random64` wraps `std::mt19937_64`. `RandomShuffle` replaces removed `std::random_shuffle`, either with caller seed or `std::random_device`.

## Control Flow
`Random::Next` computes `(seed * 16807) % (2^31 - 1)` using the Mersenne modulus reduction trick, ensuring seed zero is remapped to one. Higher-level helpers consume `Next` or uniform distributions. `Skewed` first chooses a bit-width then chooses uniformly below `2^width`.

## State And Persistence
`Random` stores a 31-bit seed in memory and can be reset. `Random32` and `Random64` store C++ standard PRNG engines. None persist state except through object lifetime; seeded construction gives reproducible streams within the same algorithm guarantees.

## Dependencies And Integration Points
Depends on `<random>`, `<algorithm>`, and RocksDB namespace. Used broadly in tests, randomized sampling, and helper utilities where speed and repeatability matter more than cryptographic quality.

## Risks
`Random::Uniform(int n)` uses modulo reduction and requires `n > 0`; callers must avoid zero and negative values except through optional helpers. `PercentTrue` calls `Uniform(100)` before comparing with the percentage, so it still consumes randomness for out-of-range percentages. `Random32` and `Random64` use standard distributions whose exact sequence can be less stable across library implementations for higher-level methods. None of these APIs are secure randomness.

## Test Signals
`random_test.cc` statistically checks `Uniform`, `OneIn`, `OneInOpt`, and `PercentTrue` over several seeds and ranges. It does not test `Random32`, `Random64`, `Skewed`, shuffle, string generation, or TLS behavior.
