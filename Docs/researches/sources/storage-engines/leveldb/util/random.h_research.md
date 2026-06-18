# sources/storage-engines/leveldb/util/random.h

## Purpose
Defines LevelDB's deterministic pseudo-random generator used by tests and internal randomized workloads. It is simple and repeatable, not cryptographic.

## Important APIs, Types, And Functions
`Random` stores a 31-bit `seed_`. `Next()` implements the Park-Miller linear congruential generator with modulus `2^31 - 1` and multiplier `16807`. `Uniform(int n)` returns `Next() % n`, `OneIn(int n)` returns true about once every `n` calls, and `Skewed(int max_log)` biases toward small values by selecting a random bit width.

## Control Flow
Construction masks the seed to 31 bits and replaces forbidden seeds `0` and `2147483647` with `1`. `Next()` multiplies in 64 bits, uses Mersenne modulus reduction, conditionally subtracts the modulus, and returns the new seed.

## State And Persistence Behavior
The generator mutates only `seed_`. It has no persistence and no synchronization; users needing reproducible sequences must control initial seed and call ordering.

## Dependencies And Integration Points
It depends only on `<cstdint>`. `util/testutil.cc` consumes it for random strings, keys, and compressible data, and many LevelDB tests use it through `test::RandomSeed()`.

## Risks And Edge Cases
`Uniform` and `OneIn` require `n > 0` but do not enforce it. Modulo reduction can introduce bias when `n` does not divide the generator period. `Skewed` uses `1 << Uniform(max_log + 1)`, so very large `max_log` values can overflow an `int` shift.

## Test Signals
There is no direct random generator test in this subset. Stable higher-level tests using seeded random data serve as regression signals for deterministic sequence changes.
