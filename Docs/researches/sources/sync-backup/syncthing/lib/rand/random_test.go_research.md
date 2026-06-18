# sources/sync-backup/syncthing/lib/rand/random_test.go

## Purpose
Basic statistical smoke tests and benchmark for the secure random convenience API.

## Important APIs, Types, and Functions
`TestRandomString` exercises `String`; `TestRandomUint64` exercises `Uint64`; `BenchmarkString` measures `String(32)`.

## Control Flow
The string test first checks exact lengths for several requested sizes, then generates 1,000 eight-character strings and compares each against all others. The uint64 test generates 1,000 numbers and similarly checks for duplicates. The benchmark repeatedly generates 32-character strings with allocation reporting.

## State and Persistence Behavior
All state is local slices of generated values. There is no persistence.

## Dependencies and Integration Points
Depends only on `testing` and the package under test. It gives confidence to callers that rely on unique random strings or numbers for test-time and runtime IDs.

## Risks and Edge Cases
Duplicate checks are probabilistic and O(n^2), though n is small. The tests are not cryptographic validation; they catch broken implementations such as fixed or heavily biased output.

## Test Signals
Passing tests indicate correct string length and plausible uniqueness for short samples of strings and uint64 values.
