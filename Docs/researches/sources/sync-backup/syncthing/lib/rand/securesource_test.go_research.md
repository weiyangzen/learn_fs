# sources/sync-backup/syncthing/lib/rand/securesource_test.go

## Purpose
Statistical smoke test and benchmark for `secureSource`.

## Important APIs, Types, and Functions
`TestSecureSource` exercises `newSecureSource` and `Int63`; `BenchmarkSecureSource` stores repeated `Int63` calls in a package-level `sink` to prevent optimization.

## Control Flow
The test samples 10,000 `Int63` values from one source and 10,000 from another, checks for no duplicates within and across samples, then counts set bits in the first sample. Bits 0-62 must be set between one-third and two-thirds of the time, while bit 63 must never be set.

## State and Persistence Behavior
All state is local sample arrays and bit counters. No persistent state exists.

## Dependencies and Integration Points
Depends on `testing`. The results support the package-level random API that relies on `secureSource`.

## Risks and Edge Cases
The test is probabilistic and intentionally not a formal randomness test. Duplicate and bit-distribution thresholds are loose but can theoretically fail by chance. The O(n^2) duplicate checks are acceptable at the sample size but not scalable.

## Test Signals
Passing tests indicate `Int63` is not constant, not obviously biased, and properly masks the high bit.
