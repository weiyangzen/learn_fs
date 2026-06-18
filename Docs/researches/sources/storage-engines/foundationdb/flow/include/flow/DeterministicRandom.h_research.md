# sources/storage-engines/foundationdb/flow/include/flow/DeterministicRandom.h

## Purpose
`DeterministicRandom.h` declares the deterministic implementation of `IRandom`, used for repeatable simulation and deterministic test behavior across compilers.

## Important APIs, Types, And Functions
`DeterministicRandom` implements `random01()`, integer and 64-bit integer ranges, `randomUInt32()`, `randomUInt64()`, `randomSkewedUInt32()`, `randomUniqueID()`, alphanumeric generation, byte filling, `truePercent()`, `peek()`, `resetSeed()`, and reference counting. It also exposes Swift retain/release shims.

## Control Flow
Calls draw from a `boost::random::mt19937_64` generator through private `gen64()`, optionally using `randLog`. Range APIs map generated values into caller-specified bounds, while `resetSeed()` reinitializes the deterministic stream.

## State And Persistence Behavior
Persistent object state is the Mersenne Twister engine, cached `next` value, and `useRandLog` flag. Reference-counted lifetime is handled through `ReferenceCounted<DeterministicRandom>`.

## Dependencies And Integration Points
It implements `IRandom`, uses `UID`, `Error`, `Trace`, `FastRef`, Boost random, and Swift C++ interop attributes. Thread-local deterministic generators are declared in `IRandom.h`.

## Risks And Edge Cases
Cross-platform determinism depends on Boost's engine rather than standard-library distributions. Range APIs must handle bounds without modulo bias or overflow in implementation. `debugRandom()` style use must avoid changing simulator determinism.

## Test Signals
Golden-seed output tests, reset reproducibility, UID uniqueness shape, range-bound checks, `truePercent()` validation, Swift retain/release compile tests, and simulator replay tests are the main signals.
